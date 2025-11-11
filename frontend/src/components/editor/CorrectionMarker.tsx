import React from 'react';
import { Correction } from '@/types/editor';

interface CorrectionMarkerProps {
  corrections: Correction[];
  onCorrectionClick?: (correction: Correction) => void;
}

export const CorrectionMarker: React.FC<CorrectionMarkerProps> = ({
  corrections,
  onCorrectionClick,
}) => {
  const getCorrectionIcon = (type: string) => {
    const icons = {
      grammar: '📝',
      spelling: '✏️',
      style: '🎨',
      punctuation: '❗',
      clarity: '💡',
      consistency: '🔄',
      compliance: '✓',
      accessibility: '♿',
    };
    return icons[type as keyof typeof icons] || '•';
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.9) return '#22c55e';
    if (confidence >= 0.7) return '#eab308';
    return '#ef4444';
  };

  return (
    <div className="correction-marker-panel">
      <h3>Corrections ({corrections.length})</h3>
      <div className="corrections-list">
        {corrections.map((correction) => (
          <div
            key={correction.id}
            className={`correction-item ${correction.status}`}
            onClick={() => onCorrectionClick?.(correction)}
            role="button"
            tabIndex={0}
            onKeyPress={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                onCorrectionClick?.(correction);
              }
            }}
          >
            <div className="correction-header">
              <span className="correction-icon">
                {getCorrectionIcon(correction.type)}
              </span>
              <span className="correction-type">{correction.type}</span>
              <span
                className="correction-confidence"
                style={{ color: getConfidenceColor(correction.confidence) }}
              >
                {(correction.confidence * 100).toFixed(0)}%
              </span>
            </div>
            <div className="correction-content">
              <div className="correction-text">
                <span className="label">Line {correction.range.startLine}:</span>
                <span className="original">{correction.original}</span>
                <span className="arrow">→</span>
                <span className="corrected">{correction.corrected}</span>
              </div>
              <p className="correction-explanation">{correction.explanation}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
