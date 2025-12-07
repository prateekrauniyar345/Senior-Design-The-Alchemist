import React, { useState } from 'react';
import { X, Brain, Thermometer, MessageSquare, Sliders } from 'lucide-react';
import './SettingsModal.css';

const SettingsModal = ({ isOpen, onClose }) => {
  const [activeSection, setActiveSection] = useState('llm');
  const [settings, setSettings] = useState({
    customPrompt: '',
    temperature: 0.7,
    maxTokens: 2048,
    topP: 1.0,
    frequencyPenalty: 0,
    presencePenalty: 0,
    model: 'gpt-4',
  });

  const handleChange = (name, value) => {
    setSettings(prev => ({ ...prev, [name]: value }));
  };

  const handleSave = () => {
    // TODO: Implement save logic later
    console.log('Saving settings:', settings);
    onClose();
  };

  if (!isOpen) return null;

  const sections = [
    { id: 'llm', label: 'LLM Settings', icon: Brain },
    { id: 'prompts', label: 'Custom Prompts', icon: MessageSquare },
    { id: 'advanced', label: 'Advanced', icon: Sliders },
  ];

  const renderContent = () => {
    switch (activeSection) {
      case 'llm':
        return (
          <div className="settings-content">
            <h3 className="settings-section-title">Language Model Configuration</h3>
            <p className="settings-section-desc">Configure the behavior of the AI model</p>

            <div className="settings-item">
              <label htmlFor="model">Model</label>
              <select
                id="model"
                value={settings.model}
                onChange={(e) => handleChange('model', e.target.value)}
                className="settings-select"
              >
                <option value="gpt-4">GPT-4</option>
                <option value="gpt-4-turbo">GPT-4 Turbo</option>
                <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
              </select>
              <span className="settings-help">Choose the AI model to use</span>
            </div>

            <div className="settings-item">
              <div className="settings-item-header">
                <label htmlFor="temperature">Temperature</label>
                <span className="settings-value">{settings.temperature}</span>
              </div>
              <input
                id="temperature"
                type="range"
                min="0"
                max="2"
                step="0.1"
                value={settings.temperature}
                onChange={(e) => handleChange('temperature', parseFloat(e.target.value))}
                className="settings-slider"
              />
              <span className="settings-help">
                Controls randomness. Lower is more focused, higher is more creative.
              </span>
            </div>

            <div className="settings-item">
              <label htmlFor="maxTokens">Max Tokens</label>
              <input
                id="maxTokens"
                type="number"
                min="256"
                max="4096"
                value={settings.maxTokens}
                onChange={(e) => handleChange('maxTokens', parseInt(e.target.value))}
                className="settings-input"
              />
              <span className="settings-help">Maximum length of the response</span>
            </div>

            <div className="settings-item">
              <div className="settings-item-header">
                <label htmlFor="topP">Top P</label>
                <span className="settings-value">{settings.topP}</span>
              </div>
              <input
                id="topP"
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={settings.topP}
                onChange={(e) => handleChange('topP', parseFloat(e.target.value))}
                className="settings-slider"
              />
              <span className="settings-help">
                Nucleus sampling. Consider tokens with top_p probability mass.
              </span>
            </div>
          </div>
        );

      case 'prompts':
        return (
          <div className="settings-content">
            <h3 className="settings-section-title">Custom System Prompt</h3>
            <p className="settings-section-desc">
              Define a custom system prompt to guide the AI's behavior
            </p>

            <div className="settings-item">
              <label htmlFor="customPrompt">System Prompt</label>
              <textarea
                id="customPrompt"
                rows="8"
                value={settings.customPrompt}
                onChange={(e) => handleChange('customPrompt', e.target.value)}
                className="settings-textarea"
                placeholder="Enter your custom system prompt here. For example: 'You are a helpful assistant specializing in geological data analysis...'"
              />
              <span className="settings-help">
                This prompt will be used to set the context for all conversations
              </span>
            </div>

            <div className="prompt-examples">
              <h4 className="prompt-examples-title">Example Prompts:</h4>
              <div className="prompt-example-item">
                <strong>Research Assistant:</strong>
                <p>"You are a knowledgeable research assistant specializing in geological sciences and mineral data analysis. Provide detailed, accurate information with citations when possible."</p>
              </div>
              <div className="prompt-example-item">
                <strong>Code Helper:</strong>
                <p>"You are an expert programmer. Help debug code, explain concepts clearly, and provide best practices for software development."</p>
              </div>
            </div>
          </div>
        );

      case 'advanced':
        return (
          <div className="settings-content">
            <h3 className="settings-section-title">Advanced Parameters</h3>
            <p className="settings-section-desc">Fine-tune model behavior with advanced settings</p>

            <div className="settings-item">
              <div className="settings-item-header">
                <label htmlFor="frequencyPenalty">Frequency Penalty</label>
                <span className="settings-value">{settings.frequencyPenalty}</span>
              </div>
              <input
                id="frequencyPenalty"
                type="range"
                min="-2"
                max="2"
                step="0.1"
                value={settings.frequencyPenalty}
                onChange={(e) => handleChange('frequencyPenalty', parseFloat(e.target.value))}
                className="settings-slider"
              />
              <span className="settings-help">
                Decreases likelihood of repeating tokens. Positive values penalize repetition.
              </span>
            </div>

            <div className="settings-item">
              <div className="settings-item-header">
                <label htmlFor="presencePenalty">Presence Penalty</label>
                <span className="settings-value">{settings.presencePenalty}</span>
              </div>
              <input
                id="presencePenalty"
                type="range"
                min="-2"
                max="2"
                step="0.1"
                value={settings.presencePenalty}
                onChange={(e) => handleChange('presencePenalty', parseFloat(e.target.value))}
                className="settings-slider"
              />
              <span className="settings-help">
                Increases likelihood of new topics. Positive values encourage variety.
              </span>
            </div>

            <div className="settings-note">
              <strong>Note:</strong> Advanced settings can significantly affect model behavior. 
              Use default values unless you understand their impact.
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="settings-modal" onClick={(e) => e.stopPropagation()}>
        <div className="settings-modal-header">
          <h2 className="settings-modal-title">Settings</h2>
          <button className="settings-close-btn" onClick={onClose} aria-label="Close">
            <X size={20} />
          </button>
        </div>

        <div className="settings-modal-body">
          {/* Left sidebar - Navigation */}
          <div className="settings-sidebar">
            {sections.map((section) => {
              const Icon = section.icon;
              return (
                <button
                  key={section.id}
                  onClick={() => setActiveSection(section.id)}
                  className={`settings-nav-item ${activeSection === section.id ? 'active' : ''}`}
                >
                  <Icon size={18} />
                  <span>{section.label}</span>
                </button>
              );
            })}
          </div>

          {/* Right content area */}
          <div className="settings-main">
            {renderContent()}
          </div>
        </div>

        <div className="settings-modal-footer">
          <button className="reset-btn" onClick={() => {
            setSettings({
              customPrompt: '',
              temperature: 0.7,
              maxTokens: 2048,
              topP: 1.0,
              frequencyPenalty: 0,
              presencePenalty: 0,
              model: 'gpt-4',
            });
          }}>
            Reset to Defaults
          </button>
          <div className="action-buttons">
            <button className="cancel-btn" onClick={onClose}>
              Cancel
            </button>
            <button className="save-btn" onClick={handleSave}>
              Save Settings
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsModal;
