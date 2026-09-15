// Frontend/src/components/chats/VegaChart.jsx
import { useEffect, useRef, useState } from 'react';
import vegaEmbed from 'vega-embed';
import { Download, SlidersHorizontal } from 'lucide-react';
import ChartSettingsModal from './ChartSettingsModal.jsx';

const actionBtn = {
  display: 'flex', alignItems: 'center', gap: '5px',
  padding: '5px 12px', fontSize: '12px', fontWeight: '500',
  borderRadius: '6px', border: '1px solid #374151',
  backgroundColor: '#1f2937', color: '#d1d5db',
  cursor: 'pointer',
};

const VegaChart = ({ spec: initialSpec, data }) => {
  const containerRef = useRef(null);
  const viewRef = useRef(null);
  const savedSpecRef = useRef(null);   // snapshot taken when modal opens
  const [error, setError] = useState(null);
  const [currentSpec, setCurrentSpec] = useState(initialSpec);
  const [showSettings, setShowSettings] = useState(false);

  useEffect(() => {
    setCurrentSpec(initialSpec);
  }, [initialSpec]);

  useEffect(() => {
    if (!containerRef.current || !currentSpec) return;
    setError(null);

    const specWithData = (data && data.length > 0)
      ? { ...currentSpec, data: { values: data } }
      : currentSpec;

    vegaEmbed(containerRef.current, specWithData, {
      actions: { export: { svg: true, png: true }, source: false, compiled: false, editor: false },
      theme: 'dark',
      background: 'transparent',
      renderer: 'svg',
    })
      .then(result => { viewRef.current = result.view; })
      .catch((err) => {
        console.error('[VegaChart] Render error:', err);
        setError(err.message || 'Failed to render chart');
      });

    return () => {
      if (containerRef.current) containerRef.current.innerHTML = '';
    };
  }, [currentSpec, data]);

  const handleDownload = () => {
    if (!viewRef.current) return;
    viewRef.current.toImageURL('png', 2).then(url => {
      const a = document.createElement('a');
      a.href = url;
      a.download = 'chart.png';
      a.click();
    }).catch(err => console.error('[VegaChart] Download error:', err));
  };

  if (!currentSpec) return null;

  return (
    <div style={{ marginTop: '8px', width: '100%' }}>
      {/* Chart container */}
      <div style={{ borderRadius: '8px', overflow: 'hidden', border: '1px solid #374151', width: '100%' }}>
        {error ? (
          <div style={{
            padding: '16px', color: '#fca5a5', fontSize: '12px',
            backgroundColor: 'rgba(127,29,29,0.2)', border: '1px solid #7f1d1d', borderRadius: '8px',
          }}>
            Chart render error: {error}
          </div>
        ) : (
          <div ref={containerRef} style={{ width: '100%', minHeight: '420px' }} />
        )}
      </div>

      {/* Action bar */}
      <div style={{ display: 'flex', gap: '8px', marginTop: '8px', flexWrap: 'wrap' }}>
        <button style={actionBtn} onClick={handleDownload}>
          <Download size={13} /> Download
        </button>
        <button
          style={{ ...actionBtn, borderColor: '#6366f1', color: '#a5b4fc' }}
          onClick={() => setShowSettings(true)}
        >
          <SlidersHorizontal size={13} /> Edit
        </button>
      </div>

      {/* Settings modal */}
      {showSettings && (
        <ChartSettingsModal
          spec={currentSpec}
          columns={data && data.length > 0 ? Object.keys(data[0]) : []}
          onPreview={(newSpec) => {
            if (!savedSpecRef.current) savedSpecRef.current = currentSpec;
            setCurrentSpec(newSpec);
          }}
          onApply={(newSpec) => {
            savedSpecRef.current = null;
            setCurrentSpec(newSpec);
            setShowSettings(false);
          }}
          onClose={() => {
            if (savedSpecRef.current) {
              setCurrentSpec(savedSpecRef.current);
              savedSpecRef.current = null;
            }
            setShowSettings(false);
          }}
        />
      )}
    </div>
  );
};

export default VegaChart;
