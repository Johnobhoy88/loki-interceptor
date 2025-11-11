import { create } from 'zustand';
import { editor } from 'monaco-editor';
import {
  EditorState,
  EditorDocument,
  Correction,
  EditorConfig,
  DocumentVersion,
  SearchResult,
} from '@/types/editor';
import { AutoSaveManager } from '@/lib/editor/autoSave';

interface EditorStore extends EditorState {
  editor: editor.IStandaloneCodeEditor | null;
  autoSaveManager: AutoSaveManager | null;

  setEditor: (editor: editor.IStandaloneCodeEditor) => void;
  setDocument: (document: EditorDocument) => void;
  updateContent: (content: string) => void;
  addCorrection: (correction: Correction) => void;
  updateCorrection: (id: string, updates: Partial<Correction>) => void;
  removeCorrection: (id: string) => void;
  selectCorrection: (correction: Correction | null) => void;
  acceptCorrection: (correction: Correction) => void;
  rejectCorrection: (correction: Correction) => void;
  updateConfig: (config: Partial<EditorConfig>) => void;
  saveDocument: () => Promise<void>;
  loadVersion: (version: DocumentVersion) => void;
  search: (query: string, options: any) => void;
  clearSearch: () => void;
  undo: () => void;
  redo: () => void;
  canUndo: boolean;
  canRedo: boolean;
}

const defaultConfig: EditorConfig = {
  theme: 'light',
  fontSize: 14,
  fontFamily: 'Consolas, Monaco, monospace',
  lineHeight: 1.6,
  tabSize: 2,
  wordWrap: true,
  minimap: true,
  lineNumbers: true,
  autoSave: true,
  autoSaveDelay: 3000,
  suggestOnTriggerCharacters: true,
  quickSuggestions: true,
  accessibilitySupport: 'auto',
};

export const useEditorStore = create<EditorStore>((set, get) => ({
  editor: null,
  document: null,
  corrections: [],
  selectedCorrection: null,
  versions: [],
  currentVersion: 1,
  isModified: false,
  isSaving: false,
  config: defaultConfig,
  searchResults: [],
  currentSearchIndex: 0,
  autoSaveManager: null,
  canUndo: false,
  canRedo: false,

  setEditor: (editor) => {
    const saveCallback = async (content: string) => {
      const { document } = get();
      if (document) {
        await get().saveDocument();
      }
    };

    const autoSaveManager = new AutoSaveManager(
      saveCallback,
      get().config.autoSaveDelay
    );

    set({ editor, autoSaveManager });
  },

  setDocument: (document) => {
    set({
      document,
      isModified: false,
      currentVersion: document.version,
      versions: [],
    });
  },

  updateContent: (content) => {
    const { document, autoSaveManager, config } = get();
    if (!document) return;

    const updatedDocument = {
      ...document,
      content,
      updatedAt: new Date(),
    };

    set({
      document: updatedDocument,
      isModified: true,
    });

    if (config.autoSave && autoSaveManager) {
      autoSaveManager.scheduleAutoSave(content);
    }
  },

  addCorrection: (correction) => {
    set((state) => ({
      corrections: [...state.corrections, correction],
    }));
  },

  updateCorrection: (id, updates) => {
    set((state) => ({
      corrections: state.corrections.map((c) =>
        c.id === id ? { ...c, ...updates } : c
      ),
    }));
  },

  removeCorrection: (id) => {
    set((state) => ({
      corrections: state.corrections.filter((c) => c.id !== id),
      selectedCorrection:
        state.selectedCorrection?.id === id ? null : state.selectedCorrection,
    }));
  },

  selectCorrection: (correction) => {
    set({ selectedCorrection: correction });
  },

  acceptCorrection: (correction) => {
    const { document, updateCorrection } = get();
    if (!document) return;

    updateCorrection(correction.id, { status: 'accepted' });

    const lines = document.content.split('\n');
    const { startLine, startColumn, endLine, endColumn } = correction.range;

    if (startLine === endLine) {
      const line = lines[startLine - 1];
      lines[startLine - 1] =
        line.substring(0, startColumn - 1) +
        correction.corrected +
        line.substring(endColumn - 1);
    }

    const newContent = lines.join('\n');
    get().updateContent(newContent);
  },

  rejectCorrection: (correction) => {
    get().updateCorrection(correction.id, { status: 'rejected' });
  },

  updateConfig: (configUpdates) => {
    const { config, editor, autoSaveManager } = get();
    const newConfig = { ...config, ...configUpdates };

    set({ config: newConfig });

    if (editor) {
      editor.updateOptions({
        wordWrap: newConfig.wordWrap ? 'on' : 'off',
        minimap: { enabled: newConfig.minimap },
        lineNumbers: newConfig.lineNumbers ? 'on' : 'off',
        fontSize: newConfig.fontSize,
        fontFamily: newConfig.fontFamily,
        lineHeight: newConfig.lineHeight,
        tabSize: newConfig.tabSize,
      });
    }

    if (autoSaveManager && configUpdates.autoSaveDelay) {
      autoSaveManager.setDelay(configUpdates.autoSaveDelay);
    }

    if (autoSaveManager && configUpdates.autoSave !== undefined) {
      autoSaveManager.setEnabled(configUpdates.autoSave);
    }
  },

  saveDocument: async () => {
    const { document } = get();
    if (!document) return;

    set({ isSaving: true });

    try {
      const version: DocumentVersion = {
        id: `v${document.version + 1}`,
        documentId: document.id,
        version: document.version + 1,
        content: document.content,
        timestamp: new Date(),
        corrections: get().corrections,
      };

      set((state) => ({
        isSaving: false,
        isModified: false,
        versions: [...state.versions, version],
        document: document
          ? {
              ...document,
              version: document.version + 1,
            }
          : null,
      }));
    } catch (error) {
      console.error('Save failed:', error);
      set({ isSaving: false });
      throw error;
    }
  },

  loadVersion: (version) => {
    const { document } = get();
    if (!document) return;

    set({
      document: {
        ...document,
        content: version.content,
        version: version.version,
      },
      corrections: version.corrections || [],
      currentVersion: version.version,
    });
  },

  search: (query, options) => {
    const { editor } = get();
    if (!editor) return;

    const model = editor.getModel();
    if (!model) return;

    const matches = model.findMatches(
      query,
      true,
      options.regex,
      options.caseSensitive,
      options.wholeWord ? '\\b' : null,
      true
    );

    const results: SearchResult[] = matches.map((match) => ({
      range: {
        startLine: match.range.startLineNumber,
        startColumn: match.range.startColumn,
        endLine: match.range.endLineNumber,
        endColumn: match.range.endColumn,
      },
      text: model.getValueInRange(match.range),
      context: model.getLineContent(match.range.startLineNumber),
    }));

    set({ searchResults: results, currentSearchIndex: 0 });
  },

  clearSearch: () => {
    set({ searchResults: [], currentSearchIndex: 0 });
  },

  undo: () => {
    const { editor } = get();
    if (editor) {
      editor.trigger('keyboard', 'undo', null);
    }
  },

  redo: () => {
    const { editor } = get();
    if (editor) {
      editor.trigger('keyboard', 'redo', null);
    }
  },
}));
