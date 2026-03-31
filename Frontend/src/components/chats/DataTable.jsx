// Frontend/src/components/chats/DataTable.jsx
import { useState } from 'react';
import { Download, Columns } from 'lucide-react';

const actionBtn = {
  display: 'flex', alignItems: 'center', gap: '5px',
  padding: '5px 12px', fontSize: '12px', fontWeight: '500',
  borderRadius: '6px', border: '1px solid #374151',
  backgroundColor: '#1f2937', color: '#d1d5db',
  cursor: 'pointer',
};

const DataTable = ({ data }) => {
  const [expanded, setExpanded] = useState(false);
  const [showColumnPicker, setShowColumnPicker] = useState(false);
  const [hiddenCols, setHiddenCols] = useState(new Set());

  if (!data || data.length === 0) return null;

  const allColumns = Object.keys(data[0]);
  const columns = allColumns.filter(c => !hiddenCols.has(c));
  const visibleRows = expanded ? data : data.slice(0, 10);

  const formatCell = (val) => {
    if (val === null || val === undefined) return '—';
    if (Array.isArray(val)) return val.join(', ');
    if (typeof val === 'object') return JSON.stringify(val);
    return String(val);
  };

  const handleDownload = () => {
    const header = allColumns.join(',');
    const rows = data.map(row =>
      allColumns.map(col => {
        const v = formatCell(row[col]);
        return v.includes(',') || v.includes('"') ? `"${v.replace(/"/g, '""')}"` : v;
      }).join(',')
    );
    const csv = [header, ...rows].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'mineral_data.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  const toggleCol = (col) => {
    setHiddenCols(prev => {
      const next = new Set(prev);
      next.has(col) ? next.delete(col) : next.add(col);
      return next;
    });
  };

  return (
    <div className="mt-2" style={{ fontSize: '12px', width: '100%' }}>
      {/* Table */}
      <div
        style={{
          width: '100%', maxHeight: '300px',
          overflowX: 'auto', overflowY: 'auto',
          borderRadius: '6px', border: '1px solid #374151', display: 'block',
        }}
      >
        <table style={{ borderCollapse: 'collapse', tableLayout: 'auto', width: '100%', minWidth: '100%' }}>
          <thead>
            <tr style={{ backgroundColor: '#1f2937' }}>
              {columns.map((col) => (
                <th
                  key={col}
                  style={{
                    padding: '7px 8px', textAlign: 'left', color: '#9ca3af',
                    fontWeight: '600', whiteSpace: 'nowrap', borderBottom: '1px solid #374151',
                    minWidth: '80px', position: 'sticky', top: 0,
                    backgroundColor: '#1f2937', zIndex: 1,
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
                      padding: '6px 8px', color: '#e5e7eb',
                      whiteSpace: 'nowrap', minWidth: '80px',
                      overflow: 'hidden', textOverflow: 'ellipsis',
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

      {/* Row count + expand toggle */}
      <div className="d-flex align-items-center justify-content-between mt-1 px-1">
        <span style={{ color: '#6b7280' }}>
          Showing {visibleRows.length} of {data.length} records
        </span>
        {data.length > 10 && (
          <button
            onClick={() => setExpanded(!expanded)}
            style={{ background: 'none', border: 'none', color: '#6366f1', cursor: 'pointer', fontSize: '12px', padding: 0 }}
          >
            {expanded ? 'Show less' : `Show all ${data.length}`}
          </button>
        )}
      </div>

      {/* Action bar */}
      <div style={{ display: 'flex', gap: '8px', marginTop: '8px', flexWrap: 'wrap' }}>
        <button style={actionBtn} onClick={handleDownload}>
          <Download size={13} /> Download
        </button>
        <button
          style={{ ...actionBtn, borderColor: '#6366f1', color: '#a5b4fc' }}
          onClick={() => setShowColumnPicker(v => !v)}
        >
          <Columns size={13} /> Edit
        </button>
      </div>

      {/* Column picker panel */}
      {showColumnPicker && (
        <div
          style={{
            marginTop: '8px', padding: '12px', borderRadius: '8px',
            border: '1px solid #374151', backgroundColor: '#111827',
            display: 'flex', flexWrap: 'wrap', gap: '8px',
          }}
        >
          <span style={{ width: '100%', fontSize: '11px', color: '#9ca3af', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Toggle columns
          </span>
          {allColumns.map(col => (
            <label
              key={col}
              style={{ display: 'flex', alignItems: 'center', gap: '5px', cursor: 'pointer', fontSize: '12px', color: '#e5e7eb' }}
            >
              <input
                type="checkbox"
                checked={!hiddenCols.has(col)}
                onChange={() => toggleCol(col)}
                style={{ cursor: 'pointer' }}
              />
              {col}
            </label>
          ))}
        </div>
      )}
    </div>
  );
};

export default DataTable;
