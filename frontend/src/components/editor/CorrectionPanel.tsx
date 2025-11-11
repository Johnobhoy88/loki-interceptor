import React, { useState } from 'react';
import { Correction } from '@/types/editor';
import { useEditorStore } from '@/hooks/useEditor';

interface CorrectionPanelProps {
  correction: Correction;
  onAccept: (correction: Correction) => void;
  onReject: (correction: Correction) => void;
  onClose: () => void;
}

export const CorrectionPanel: React.FC<CorrectionPanelProps> = ({
  correction,
  onAccept,
  onReject,
  onClose,
}) => {
  const [note, setNote] = useState('');

  const handleAccept = () => {
    onAccept(correction);
    onClose();
  };

  const handleReject = () => {
    onReject(correction);
    onClose();
  };

  const confidenceColor =
    correction.confidence >= 0.9
      ? 'high'
      : correction.confidence >= 0.7
      ? 'medium'
      : 'low';

  return (
    <div className="correction-panel">
      <div className="panel-header">
        <h3>Correction Details</h3>
        <button onClick={onClose} aria-label="Close panel">
          ✕
        </button>
      </div>

      <div className="panel-content">
        <div className="correction-meta">
          <span className="type-badge">{correction.type}</span>
          <span className={`confidence-badge ${confidenceColor}`}>
            {(correction.confidence * 100).toFixed(0)}% confidence
          </span>
        </div>

        <div className="correction-location">
          <strong>Location:</strong> Line {correction.range.startLine}, Column{' '}
          {correction.range.startColumn}
        </div>

        <div className="correction-comparison">
          <div className="original">
            <label>Original:</label>
            <code>{correction.original}</code>
          </div>
          <div className="arrow">→</div>
          <div className="corrected">
            <label>Suggested:</label>
            <code>{correction.corrected}</code>
          </div>
        </div>

        <div className="correction-explanation">
          <strong>Explanation:</strong>
          <p>{correction.explanation}</p>
        </div>

        {correction.metadata?.rule && (
          <div className="correction-rule">
            <strong>Rule:</strong> {correction.metadata.rule}
          </div>
        )}

        {correction.metadata?.links && correction.metadata.links.length > 0 && (
          <div className="correction-links">
            <strong>Learn more:</strong>
            <ul>
              {correction.metadata.links.map((link, idx) => (
                <li key={idx}>
                  <a href={link} target="_blank" rel="noopener noreferrer">
                    {link}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        )}

        <div className="correction-note">
          <label htmlFor="correction-note">Add a note (optional):</label>
          <textarea
            id="correction-note"
            value={note}
            onChange={(e) => setNote(e.target.value)}
            placeholder="Add any additional notes about this correction..."
            rows={3}
          />
        </div>
      </div>

      <div className="panel-actions">
        <button onClick={handleReject} className="btn-reject">
          Reject
        </button>
        <button onClick={handleAccept} className="btn-accept">
          Accept & Apply
        </button>
      </div>
    </div>
  );
};
