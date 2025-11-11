import React from 'react';
import { editor } from 'monaco-editor';
import { useEditorStore } from '@/hooks/useEditor';

interface EditorToolbarProps {
  editor: editor.IStandaloneCodeEditor | null;
}

export const EditorToolbar: React.FC<EditorToolbarProps> = ({ editor }) => {
  const { config, updateConfig, undo, redo, canUndo, canRedo } = useEditorStore();

  const handleUndo = () => {
    if (editor && canUndo) {
      editor.trigger('toolbar', 'undo', null);
      undo();
    }
  };

  const handleRedo = () => {
    if (editor && canRedo) {
      editor.trigger('toolbar', 'redo', null);
      redo();
    }
  };

  const handleFormat = () => {
    if (editor) {
      editor.trigger('toolbar', 'editor.action.formatDocument', null);
    }
  };

  const handleToggleWordWrap = () => {
    updateConfig({ wordWrap: !config.wordWrap });
  };

  const handleToggleMinimap = () => {
    updateConfig({ minimap: !config.minimap });
  };

  return (
    <div className="editor-toolbar">
      <div className="toolbar-section">
        <button 
          onClick={handleUndo} 
          disabled={!canUndo}
          title="Undo (Ctrl+Z)"
          aria-label="Undo"
        >
          ↶ Undo
        </button>
        <button 
          onClick={handleRedo} 
          disabled={!canRedo}
          title="Redo (Ctrl+Y)"
          aria-label="Redo"
        >
          ↷ Redo
        </button>
      </div>
      <div className="toolbar-section">
        <button 
          onClick={handleFormat}
          title="Format Document (Shift+Alt+F)"
          aria-label="Format Document"
        >
          ⚡ Format
        </button>
        <button 
          onClick={handleToggleWordWrap}
          title="Toggle Word Wrap"
          aria-label="Toggle Word Wrap"
          className={config.wordWrap ? 'active' : ''}
        >
          ⮐ Word Wrap
        </button>
        <button 
          onClick={handleToggleMinimap}
          title="Toggle Minimap"
          aria-label="Toggle Minimap"
          className={config.minimap ? 'active' : ''}
        >
          ⊟ Minimap
        </button>
      </div>
    </div>
  );
};
