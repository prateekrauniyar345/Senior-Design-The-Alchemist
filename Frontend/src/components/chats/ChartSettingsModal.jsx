// Frontend/src/components/chats/ChartSettingsModal.jsx
import { useState, useEffect, useRef } from 'react';
import { X } from 'lucide-react';

const MARK_TYPES = ['bar', 'line', 'point', 'area', 'rect', 'arc', 'tick', 'rule'];
const FIELD_TYPES = ['quantitative', 'nominal', 'ordinal', 'temporal'];
const AGGREGATES = ['none', 'count', 'mean', 'sum', 'min', 'max', 'median'];
const COLOR_SCHEMES = ['tableau10', 'category10', 'set1', 'pastel1', 'dark2', 'viridis', 'blues', 'reds', 'oranges', 'greens'];

// ── Helpers ────────────────────────────────────────────────────────────────
const extractSettings = (spec) => {
  const enc = spec.encoding || {};
  const x = enc.x || {};
  const y = enc.y || {};
  const color = enc.color || {};
  return {
    markType: typeof spec.mark === 'string' ? spec.mark : (spec.mark?.type || 'bar'),
    title: typeof spec.title === 'string' ? spec.title : (spec.title?.text || ''),
    height: spec.height || 400,
    transform: spec.transform || null,   // preserve LLM-generated transforms
    xField: x.field || '',
    xType: x.type || 'quantitative',
    xBin: !!x.bin,
    xAggregate: x.aggregate || 'none',
    xTitle: x.title || '',
    yField: y.field || '',
    yType: y.type || 'quantitative',
    yAggregate: y.aggregate || 'none',
    yTitle: y.title || '',
    colorField: color.field || '',
    colorType: color.type || 'nominal',
    colorScheme: color.scale?.scheme || 'tableau10',
    colorValue: (typeof color.value === 'string') ? color.value : '#4C78A8',
    useColorField: !!color.field,
  };
};

const buildSpec = (s) => {
  const xEncoding = {
    ...(s.xField ? { field: s.xField } : {}),
    type: s.xType,
    ...(s.xBin ? { bin: true } : {}),
    ...(s.xAggregate !== 'none' ? { aggregate: s.xAggregate } : {}),
    title: s.xTitle || s.xField || undefined,
  };

  const yEncoding = s.yAggregate !== 'none'
    ? { aggregate: s.yAggregate, type: 'quantitative', title: s.yTitle || s.yAggregate }
    : { field: s.yField, type: s.yType, title: s.yTitle || s.yField || undefined };

  const colorEncoding = s.useColorField && s.colorField
    ? { field: s.colorField, type: s.colorType, scale: { scheme: s.colorScheme } }
    : { value: s.colorValue };

  const tooltipFields = [
    s.xField && { field: s.xField, type: s.xType },
    s.yField && { field: s.yField, type: s.yType },
  ].filter(Boolean);

  return {
    $schema: 'https://vega.github.io/schema/vega-lite/v5.json',
    title: s.title || undefined,
    data: { name: 'table' },
    ...(s.transform ? { transform: s.transform } : {}),
    width: 'container',
    height: Number(s.height) || 400,
    mark: { type: s.markType, opacity: 0.85 },
    encoding: {
      x: xEncoding,
      y: yEncoding,
      color: colorEncoding,
      ...(tooltipFields.length > 0 ? { tooltip: tooltipFields } : {}),
    },
  };
};

// ── Styled sub-components ──────────────────────────────────────────────────
const Label = ({ children }) => (
  <label style={{ fontSize: '11px', color: '#ffffff', fontWeight: '600',
    textTransform: 'uppercase', letterSpacing: '0.05em', display: 'block', marginBottom: '4px' }}>
    {children}
  </label>
);

const Select = ({ value, onChange, children, style }) => (
  <select
    value={value}
    onChange={e => onChange(e.target.value)}
    style={{
      width: '100%', padding: '6px 8px', borderRadius: '6px', fontSize: '12px',
      backgroundColor: '#4b5563', border: '1px solid #6b7280', color: '#ffffff',
      cursor: 'pointer', ...style,
    }}
  >
    {children}
  </select>
);

const Input = ({ value, onChange, placeholder, type = 'text' }) => (
  <input
    type={type}
    value={value}
    onChange={e => onChange(e.target.value)}
    placeholder={placeholder}
    style={{
      width: '100%', padding: '6px 8px', borderRadius: '6px', fontSize: '12px',
      backgroundColor: '#4b5563', border: '1px solid #6b7280', color: '#ffffff',
      boxSizing: 'border-box',
    }}
  />
);

const SectionTitle = ({ children }) => (
  <p style={{ fontSize: '12px', fontWeight: '700', color: '#a5b4fc',
    borderBottom: '1px solid #374151', paddingBottom: '6px', marginBottom: '10px', marginTop: '16px' }}>
    {children}
  </p>
);

// ── Main Component ─────────────────────────────────────────────────────────
const ChartSettingsModal = ({ spec, columns, onApply, onPreview, onClose }) => {
  const [settings, setSettings] = useState(() => extractSettings(spec));
  const isMounted = useRef(false);

  const set = (key, val) => setSettings(prev => ({ ...prev, [key]: val }));

  // Live preview — skip the very first render (initial state matches current spec)
  useEffect(() => {
    if (!isMounted.current) { isMounted.current = true; return; }
    if (onPreview) onPreview(buildSpec(settings));
  }, [settings]);

  const colOptions = ['', ...columns].map(c => (
    <option key={c} value={c}>{c || '— none —'}</option>
  ));

  const handleApply = () => {
    onApply(buildSpec(settings));
  };

  return (
    // Backdrop
    <div
      onClick={onClose}
      style={{
        position: 'fixed', inset: 0, zIndex: 1000,
        backgroundColor: 'rgba(0,0,0,0.5)',
        display: 'flex', justifyContent: 'flex-end',
      }}
    >
      {/* Panel — stop click propagation so backdrop click closes but panel clicks don't */}
      <div
        onClick={e => e.stopPropagation()}
        style={{
          width: '320px', height: '100vh', overflowY: 'auto',
          backgroundColor: '#161618', borderLeft: '1px solid #334155',
          padding: '20px', display: 'flex', flexDirection: 'column', gap: '4px',
          boxShadow: '-8px 0 32px rgba(0,0,0,0.6)',
        }}
      >
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
          <span style={{ fontWeight: '700', color: '#ffffff', fontSize: '14px' }}>Customize Chart</span>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer', padding: '2px' }}>
            <X size={18} />
          </button>
        </div>
        <p style={{ fontSize: '11px', color: '#94a3b8', marginBottom: '8px' }}>
          Adjust fields, mark type, colors, and layout.
        </p>

        {/* ── Chart */}
        <SectionTitle>Chart</SectionTitle>
        <div style={{ marginBottom: '10px' }}>
          <Label>Title</Label>
          <Input value={settings.title} onChange={v => set('title', v)} placeholder="Chart title..." />
        </div>
        <div style={{ marginBottom: '10px' }}>
          <Label>Mark type</Label>
          <Select value={settings.markType} onChange={v => set('markType', v)}>
            {MARK_TYPES.map(m => <option key={m} value={m}>{m}</option>)}
          </Select>
        </div>
        <div style={{ marginBottom: '10px' }}>
          <Label>Height (px)</Label>
          <Input type="number" value={settings.height} onChange={v => set('height', v)} placeholder="400" />
        </div>

        {/* ── X Axis */}
        <SectionTitle>X Axis</SectionTitle>
        <div style={{ marginBottom: '8px' }}>
          <Label>Field</Label>
          <Select value={settings.xField} onChange={v => set('xField', v)}>{colOptions}</Select>
        </div>
        <div style={{ marginBottom: '8px' }}>
          <Label>Type</Label>
          <Select value={settings.xType} onChange={v => set('xType', v)}>
            {FIELD_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
          </Select>
        </div>
        <div style={{ marginBottom: '8px' }}>
          <Label>Aggregate</Label>
          <Select value={settings.xAggregate} onChange={v => set('xAggregate', v)}>
            {AGGREGATES.map(a => <option key={a} value={a}>{a}</option>)}
          </Select>
        </div>
        <div style={{ marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <input type="checkbox" id="xBin" checked={settings.xBin} onChange={e => set('xBin', e.target.checked)} />
          <label htmlFor="xBin" style={{ fontSize: '12px', color: '#ffffff', cursor: 'pointer' }}>
            Bin (histogram)
          </label>
        </div>
        <div style={{ marginBottom: '8px' }}>
          <Label>Axis label</Label>
          <Input value={settings.xTitle} onChange={v => set('xTitle', v)} placeholder={settings.xField || 'X axis label'} />
        </div>

        {/* ── Y Axis */}
        <SectionTitle>Y Axis</SectionTitle>
        <div style={{ marginBottom: '8px' }}>
          <Label>Field</Label>
          <Select value={settings.yField} onChange={v => set('yField', v)}>{colOptions}</Select>
        </div>
        <div style={{ marginBottom: '8px' }}>
          <Label>Type</Label>
          <Select value={settings.yType} onChange={v => set('yType', v)}>
            {FIELD_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
          </Select>
        </div>
        <div style={{ marginBottom: '8px' }}>
          <Label>Aggregate</Label>
          <Select value={settings.yAggregate} onChange={v => set('yAggregate', v)}>
            {AGGREGATES.map(a => <option key={a} value={a}>{a}</option>)}
          </Select>
        </div>
        <div style={{ marginBottom: '8px' }}>
          <Label>Axis label</Label>
          <Input value={settings.yTitle} onChange={v => set('yTitle', v)} placeholder={settings.yField || 'Y axis label'} />
        </div>

        {/* ── Color */}
        <SectionTitle>Color</SectionTitle>
        <div style={{ marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <input type="checkbox" id="useColorField" checked={settings.useColorField}
            onChange={e => set('useColorField', e.target.checked)} />
          <label htmlFor="useColorField" style={{ fontSize: '12px', color: '#ffffff', cursor: 'pointer' }}>
            Color by field
          </label>
        </div>
        {settings.useColorField ? (
          <>
            <div style={{ marginBottom: '8px' }}>
              <Label>Color field</Label>
              <Select value={settings.colorField} onChange={v => set('colorField', v)}>{colOptions}</Select>
            </div>
            <div style={{ marginBottom: '8px' }}>
              <Label>Field type</Label>
              <Select value={settings.colorType} onChange={v => set('colorType', v)}>
                {FIELD_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
              </Select>
            </div>
            <div style={{ marginBottom: '8px' }}>
              <Label>Color scheme</Label>
              <Select value={settings.colorScheme} onChange={v => set('colorScheme', v)}>
                {COLOR_SCHEMES.map(s => <option key={s} value={s}>{s}</option>)}
              </Select>
            </div>
          </>
        ) : (
          <div style={{ marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Label>Solid color</Label>
            <input type="color" value={settings.colorValue}
              onChange={e => set('colorValue', e.target.value)}
              style={{ width: '40px', height: '28px', border: 'none', borderRadius: '4px', cursor: 'pointer', backgroundColor: 'transparent' }} />
            <span style={{ fontSize: '12px', color: '#ffffff' }}>{settings.colorValue}</span>
          </div>
        )}

        {/* ── Apply */}
        <div style={{ marginTop: 'auto', paddingTop: '16px', display: 'flex', gap: '8px' }}>
          <button
            onClick={handleApply}
            style={{
              flex: 1, padding: '8px', borderRadius: '6px', border: 'none',
              backgroundColor: '#6366f1', color: '#fff', fontWeight: '600',
              fontSize: '13px', cursor: 'pointer',
            }}
          >
            Apply
          </button>
          <button
            onClick={onClose}
            style={{
              padding: '8px 16px', borderRadius: '6px',
              border: '1px solid #475569', backgroundColor: '#1e293b',
              color: '#ffffff', fontSize: '13px', cursor: 'pointer',
            }}
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChartSettingsModal;
