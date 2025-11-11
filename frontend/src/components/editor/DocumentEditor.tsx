import React, { useRef, useCallback, useEffect } from 'react';
import Editor, { Monaco, OnMount } from '@monaco-editor/react';
import { editor } from 'monaco-editor';
import { EditorDocument, Correction, EditorConfig } from '@/types/editor';
import { useEditorStore } from '@/hooks/useEditor';
import { CorrectionMarker } from './CorrectionMarker';
import { EditorToolbar } from './EditorToolbar';
import { EditorStatusBar } from './EditorStatusBar';
import './DocumentEditor.css';

interface DocumentEditorProps {
  document: EditorDocument;
  corrections?: Correction[];
  config?: Partial<EditorConfig>;
  onContentChange?: (content: string) => void;
  onCorrectionClick?: (correction: Correction) => void;
  readOnly?: boolean;
}

export const DocumentEditor: React.FC<DocumentEditorProps> = ({
  document,
  corrections = [],
  config,
  onContentChange,
  onCorrectionClick,
  readOnly = false,
}) => {
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);
  const monacoRef = useRef<Monaco | null>(null);
  const decorationsRef = useRef<string[]>([]);

  const { setEditor, updateConfig } = useEditorStore();

  const handleEditorDidMount: OnMount = useCallback((editor, monaco) => {
    editorRef.current = editor;
    monacoRef.current = monaco;
    setEditor(editor);

    editor.updateOptions({
      readOnly,
      minimap: { enabled: config?.minimap ?? true },
      lineNumbers: config?.lineNumbers ? 'on' : 'off',
      wordWrap: config?.wordWrap ? 'on' : 'off',
      fontSize: config?.fontSize ?? 14,
      fontFamily: config?.fontFamily ?? 'Consolas, Monaco, monospace',
      lineHeight: config?.lineHeight ?? 1.6,
      tabSize: config?.tabSize ?? 2,
      quickSuggestions: config?.quickSuggestions ?? true,
      suggestOnTriggerCharacters: config?.suggestOnTriggerCharacters ?? true,
      accessibilitySupport: config?.accessibilitySupport ?? 'auto',
    });

    registerKeyboardShortcuts(editor, monaco);

    if (corrections.length > 0) {
      applyCorrectionsAsDecorations(editor, monaco, corrections);
    }
  }, [config, readOnly, corrections, setEditor]);

  const handleEditorChange = useCallback(
    (value: string | undefined) => {
      if (value !== undefined && onContentChange) {
        onContentChange(value);
      }
    },
    [onContentChange]
  );

  const applyCorrectionsAsDecorations = useCallback(
    (
      editor: editor.IStandaloneCodeEditor,
      monaco: Monaco,
      corrections: Correction[]
    ) => {
      const newDecorations: editor.IModelDeltaDecoration[] = corrections.map(
        (correction) => {
          const confidenceLevel = Math.floor(correction.confidence * 10);
          const confidencePercent = (correction.confidence * 100).toFixed(0);
          return {
            range: new monaco.Range(
              correction.range.startLine,
              correction.range.startColumn,
              correction.range.endLine,
              correction.range.endColumn
            ),
            options: {
              className: `correction-${correction.type} correction-confidence-${confidenceLevel}`,
              hoverMessage: {
                value: `**${correction.type.toUpperCase()}** (${confidencePercent}%)\\n\\n${correction.explanation}\\n\\n*Original:* ${correction.original}\\n*Suggested:* ${correction.corrected}`,
              },
              glyphMarginClassName: `glyph-${correction.type}`,
              inlineClassName: `inline-correction-${correction.status}`,
            },
          };
        }
      );

      decorationsRef.current = editor.deltaDecorations(
        decorationsRef.current,
        newDecorations
      );
    },
    []
  );

  const registerKeyboardShortcuts = useCallback(
    (editor: editor.IStandaloneCodeEditor, monaco: Monaco) => {
      editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
        const content = editor.getValue();
        console.log('Save triggered', content);
      });

      editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyF, () => {
        editor.trigger('keyboard', 'actions.find', {});
      });

      editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyH, () => {
        editor.trigger('keyboard', 'editor.action.startFindReplaceAction', {});
      });

      editor.addCommand(
        monaco.KeyMod.Shift | monaco.KeyMod.Alt | monaco.KeyCode.KeyF,
        () => {
          editor.trigger('keyboard', 'editor.action.formatDocument', {});
        }
      );
    },
    []
  );

  useEffect(() => {
    if (editorRef.current && monacoRef.current && corrections.length > 0) {
      applyCorrectionsAsDecorations(
        editorRef.current,
        monacoRef.current,
        corrections
      );
    }
  }, [corrections, applyCorrectionsAsDecorations]);

  return (
    <div className="document-editor-container">
      <EditorToolbar editor={editorRef.current} />
      <div className="editor-wrapper">
        <Editor
          height="calc(100vh - 120px)"
          language={document.language || 'markdown'}
          value={document.content}
          onChange={handleEditorChange}
          onMount={handleEditorDidMount}
          theme={config?.theme === 'dark' ? 'vs-dark' : 'vs'}
          options={{
            automaticLayout: true,
            scrollBeyondLastLine: false,
            renderWhitespace: 'selection',
            bracketPairColorization: { enabled: true },
            guides: {
              bracketPairs: true,
              indentation: true,
            },
          }}
        />
        {corrections.length > 0 && (
          <CorrectionMarker
            corrections={corrections}
            onCorrectionClick={onCorrectionClick}
          />
        )}
      </div>
      <EditorStatusBar
        document={document}
        corrections={corrections}
        editor={editorRef.current}
      />
    </div>
  );
};

export default DocumentEditor;
