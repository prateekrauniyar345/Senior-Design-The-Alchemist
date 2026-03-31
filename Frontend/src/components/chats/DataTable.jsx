// Frontend/src/components/chats/DataTable.jsx
import React, { useState } from 'react';

const DataTable = ({ data }) => {
  const [expanded, setExpanded] = useState(false);

  if (!data || data.length === 0) return null;

  const columns = Object.keys(data[0]);
  const visibleRows = expanded ? data : data.slice(0, 10);

  const formatCell = (val) => {
    if (val === null || val === undefined) return '—';
    if (Array.isArray(val)) return val.join(', ');
    if (typeof val === 'object') return JSON.stringify(val);
    return String(val);
  };

  return (
    <div className="mt-2" style={{ fontSize: '12px', width: '100%' }}>
      <div
        style={{
          width: '100%',
          maxHeight: '300px',
          overflowX: 'auto',
          overflowY: 'auto',
          borderRadius: '6px',
          border: '1px solid #374151',
          display: 'block',
        }}
      >
        <table style={{ borderCollapse: 'collapse', tableLayout: 'auto', width: '100%', minWidth: '100%' }}>
          <thead>
            <tr style={{ backgroundColor: '#1f2937' }}>
              {columns.map((col) => (
                <th
                  key={col}
                  style={{
                    padding: '7px 8px',
                    textAlign: 'left',
                    color: '#9ca3af',
                    fontWeight: '600',
                    whiteSpace: 'nowrap',
                    borderBottom: '1px solid #374151',
                    minWidth: '80px',
                    position: 'sticky',
                    top: 0,
                    backgroundColor: '#1f2937',
                    zIndex: 1,
                  }}
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {visibleRows.map((row, i) => (
              <tr
                key={i}
                style={{
                  backgroundColor: i % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.02)',
                  borderBottom: '1px solid #1f2937',
                }}
              >
                {columns.map((col) => (
                  <td
                    key={col}
                    style={{
                      padding: '6px 8px',
                      color: '#e5e7eb',
                      whiteSpace: 'nowrap',
                      minWidth: '80px',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                    }}
                    title={formatCell(row[col])}
                  >
                    {formatCell(row[col])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="d-flex align-items-center justify-content-between mt-1 px-1">
        <span style={{ color: '#6b7280' }}>
          Showing {visibleRows.length} of {data.length} records
        </span>
        {data.length > 10 && (
          <button
            onClick={() => setExpanded(!expanded)}
            style={{
              background: 'none',
              border: 'none',
              color: '#6366f1',
              cursor: 'pointer',
              fontSize: '12px',
              padding: 0,
            }}
          >
            {expanded ? 'Show less' : `Show all ${data.length}`}
          </button>
        )}
      </div>
    </div>
  );
};

export default DataTable;
