import React, { useState, useRef } from 'react';
import { DocumentEditor } from '@/components/editor/DocumentEditor';
import { SearchReplace } from '@/components/editor/SearchReplace';
import { EditorDocument } from '@/types/editor';
import { editor } from 'monaco-editor';

export const SearchReplaceExample: React.FC = () => {
  const [document] = useState<EditorDocument>({
    id: '1',
    title: 'Search and Replace Demo',
    content: `The quick brown fox jumps over the lazy dog.
The quick brown fox is very quick.
Fox is a quick animal.`,
    language: 'text',
    version: 1,
    createdAt: new Date(),
    updatedAt: new Date(),
  });

  const [showSearch, setShowSearch] = useState(false);
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);

  return (
    <div style={{ height: '100vh', position: 'relative' }}>
      <button
        onClick={() => setShowSearch(!showSearch)}
        style={{ position: 'absolute', top: '10px', right: '10px', zIndex: 101 }}
      >
        {showSearch ? 'Hide' : 'Show'} Search
      </button>

      <DocumentEditor
        document={document}
        onContentChange={(content) => console.log('Content:', content)}
      />

      {showSearch && (
        <SearchReplace
          editor={editorRef.current}
          onClose={() => setShowSearch(false)}
        />
      )}
    </div>
  );
};
