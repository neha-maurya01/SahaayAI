// Configuration
const API_BASE_URL = 'http://localhost:8000';
const DEFAULT_PHONE = '+919876543210'; // Demo phone number

// State management
let conversationId = null;
let currentLanguage = 'en';
let isLoading = false;
let audioEnabled = true;
let conversationHistory = [];
let userSettings = {
    district: '',
    state: '',
    literacyLevel: 'medium',
    autoPlayAudio: false,
    slowSpeech: false
};
let knowledgeBaseSchemes = [];

// DOM Elements
const welcomeSection = document.getElementById('welcomeSection');
const chatSection = document.getElementById('chatSection');
const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const languageSelect = document.getElementById('languageSelect');
const audioToggleBtn = document.getElementById('audioToggleBtn');
const historyBtn = document.getElementById('historyBtn');
const infoBtn = document.getElementById('infoBtn');
const settingsBtn = document.getElementById('settingsBtn');
const homeBtn = document.getElementById('homeBtn');
const browseSchemes = document.getElementById('browseSchemes');
const infoModal = document.getElementById('infoModal');
const historyModal = document.getElementById('historyModal');
const settingsModal = document.getElementById('settingsModal');
const schemeModal = document.getElementById('schemeModal');
const closeModal = document.getElementById('closeModal');
const closeHistoryModal = document.getElementById('closeHistoryModal');
const closeSettingsModal = document.getElementById('closeSettingsModal');
const closeSchemeModal = document.getElementById('closeSchemeModal');
const statusIndicator = document.getElementById('statusIndicator');
const statusText = document.getElementById('statusText');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    checkAPIHealth();
    loadSettings();
    loadKnowledgeBase();
    
    // Set initial audio button style
    if (audioEnabled) {
        audioToggleBtn.style.background = 'rgba(16, 185, 129, 0.1)';
        audioToggleBtn.style.borderColor = 'var(--secondary-color)';
    }
});

// Event Listeners
function setupEventListeners() {
    // Send message
    sendBtn.addEventListener('click', handleSendMessage);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    });

    // Language selection
    languageSelect.addEventListener('change', (e) => {
        currentLanguage = e.target.value;
        console.log('Language changed to:', currentLanguage);
    });

    // Quick query suggestions
    document.querySelectorAll('.suggestion-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const query = this.getAttribute('data-query');
            if (query) {
                messageInput.value = query;
                handleSendMessage();
            }
        });
    });

    // Feature cards
    document.querySelectorAll('.feature-card').forEach(card => {
        card.addEventListener('click', function(e) {
            e.preventDefault();
            const query = this.getAttribute('data-query');
            if (query) {
                messageInput.value = query;
                handleSendMessage();
            }
        });
    });

    // Audio toggle
    audioToggleBtn.addEventListener('click', () => {
        audioEnabled = !audioEnabled;
        audioToggleBtn.querySelector('span').textContent = audioEnabled ? '🔊' : '🔇';
        audioToggleBtn.title = audioEnabled ? 'Disable Audio Responses' : 'Enable Audio Responses';
        
        // Add visual feedback
        if (audioEnabled) {
            audioToggleBtn.style.background = 'rgba(16, 185, 129, 0.1)';
            audioToggleBtn.style.borderColor = 'var(--secondary-color)';
        } else {
            audioToggleBtn.style.background = 'var(--bg-primary)';
            audioToggleBtn.style.borderColor = 'var(--border-color)';
        }
        
        console.log('Audio responses:', audioEnabled ? 'enabled' : 'disabled');
    });

    // History modal
    historyBtn.addEventListener('click', () => {
        showConversationHistory();
        historyModal.classList.add('active');
    });

    closeHistoryModal.addEventListener('click', () => {
        historyModal.classList.remove('active');
    });

    historyModal.addEventListener('click', (e) => {
        if (e.target === historyModal) {
            historyModal.classList.remove('active');
        }
    });

    // Info modal
    infoBtn.addEventListener('click', () => {
        infoModal.classList.add('active');
    });

    closeModal.addEventListener('click', () => {
        infoModal.classList.remove('active');
    });

    infoModal.addEventListener('click', (e) => {
        if (e.target === infoModal) {
            infoModal.classList.remove('active');
        }
    });

    // Settings button
    settingsBtn.addEventListener('click', () => {
        settingsModal.style.display = 'flex';
        populateSettings();
    });

    closeSettingsModal.addEventListener('click', () => {
        settingsModal.style.display = 'none';
    });

    // Home button - go back to welcome screen
    homeBtn.addEventListener('click', () => {
        goToHome();
    });

    // Browse schemes button
    browseSchemes.addEventListener('click', () => {
        schemeModal.style.display = 'flex';
        displaySchemes(knowledgeBaseSchemes);
    });

    closeSchemeModal.addEventListener('click', () => {
        schemeModal.style.display = 'none';
    });

    // Save settings
    document.getElementById('saveSettings').addEventListener('click', saveSettings);
    document.getElementById('resetSettings').addEventListener('click', resetSettings);

    // Scheme search
    document.getElementById('searchSchemes').addEventListener('click', searchSchemes);
    document.getElementById('schemeSearch').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            searchSchemes();
        }
    });

    // Domain filter chips
    document.querySelectorAll('.chip').forEach(chip => {
        chip.addEventListener('click', () => {
            document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
            chip.classList.add('active');
            filterSchemesByDomain(chip.dataset.domain);
        });
    });

    // Close modals on outside click
    window.addEventListener('click', (e) => {
        if (e.target === settingsModal) settingsModal.style.display = 'none';
        if (e.target === schemeModal) schemeModal.style.display = 'none';
    });
}

// Check API Health
async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            updateStatus('connected', 'Connected');
        } else {
            updateStatus('error', 'API Error');
        }
    } catch (error) {
        console.error('Health check failed:', error);
        updateStatus('error', 'Disconnected');
    }
}

// Update connection status
function updateStatus(status, text) {
    statusText.textContent = text;
    if (status === 'error') {
        statusIndicator.classList.add('error');
    } else {
        statusIndicator.classList.remove('error');
    }
}

// Handle send message
async function handleSendMessage() {
    const message = messageInput.value.trim();
    
    if (!message || isLoading) return;

    // Validate message content before sending
    const validation = validateMessageContent(message);
    if (!validation.isValid) {
        addMessage(message, 'user');
        addMessage(validation.message, 'assistant');
        messageInput.value = '';
        return;
    }

    // Show chat section if hidden
    if (welcomeSection.style.display !== 'none') {
        welcomeSection.style.display = 'none';
        chatSection.style.display = 'block';
        homeBtn.style.display = 'block'; // Show home button when chat starts
    }

    // Add user message to chat
    addMessage(message, 'user');
    
    // Clear input
    messageInput.value = '';
    
    // Disable input while processing
    setLoading(true);

    // Show loading indicator
    const loadingId = addLoadingIndicator();

    try {
        // Send message to API
        const response = await fetch(`${API_BASE_URL}/api/v1/message/web`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                phone_number: DEFAULT_PHONE,
                language: currentLanguage
            })
        });

        // Remove loading indicator
        removeLoadingIndicator(loadingId);

        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }

        const data = await response.json();
        
        // Update conversation ID
        if (data.conversation_id) {
            conversationId = data.conversation_id;
        }

        // Add assistant response
        if (data.success && data.response) {
            addAssistantResponse(data.response);
        } else {
            throw new Error('Invalid response format');
        }

    } catch (error) {
        console.error('Error sending message:', error);
        removeLoadingIndicator(loadingId);
        
        // Show error message
        addMessage(
            "I apologize, but I'm having trouble processing your request right now. Please try again in a moment.",
            'assistant'
        );
        
        updateStatus('error', 'Connection Error');
    } finally {
        setLoading(false);
    }
}

// Add user/assistant message
function addMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = sender === 'user' ? '👤' : '🤖';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const bubbleDiv = document.createElement('div');
    bubbleDiv.className = 'message-bubble';
    bubbleDiv.textContent = text;
    
    const timeDiv = document.createElement('div');
    timeDiv.className = 'message-time';
    timeDiv.textContent = new Date().toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    
    contentDiv.appendChild(bubbleDiv);
    contentDiv.appendChild(timeDiv);
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();

    // Store user message in conversation history
    if (sender === 'user') {
        conversationHistory.push({
            timestamp: new Date(),
            type: 'user',
            message: text
        });
    }
}

// Add assistant response with action plan
function addAssistantResponse(response) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = '🤖';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // If we have an action plan, show a friendly intro message instead of technical text
    if (response.action_plan) {
        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = 'message-bubble';
        bubbleDiv.textContent = "I've created a personalized action plan for you. Let me guide you through the steps!";
        contentDiv.appendChild(bubbleDiv);
        
        // Then show the action plan
        const actionPlanDiv = createActionPlan(response.action_plan);
        contentDiv.appendChild(actionPlanDiv);
    } else if (response.text) {
        // For simple responses without action plan, show the text
        // Check if it's a guardrail message (contains warning emoji or multiple bullet points)
        const isGuardrailMessage = response.text.includes('⚠️') || 
                                   response.text.includes('🤔') || 
                                   response.text.includes('👋') ||
                                   (response.text.match(/•/g) || []).length >= 3;
        
        if (isGuardrailMessage) {
            // Format guardrail message with proper styling
            const formattedMessage = formatGuardrailMessage(response.text);
            
            // Add appropriate class based on message type
            if (response.text.includes('⚠️')) {
                formattedMessage.classList.add('warning');
            } else if (response.text.includes('🤔') || response.text.includes('👋')) {
                formattedMessage.classList.add('info');
            }
            
            contentDiv.appendChild(formattedMessage);
        } else {
            // Regular text response
            const bubbleDiv = document.createElement('div');
            bubbleDiv.className = 'message-bubble';
            bubbleDiv.textContent = response.text;
            contentDiv.appendChild(bubbleDiv);
        }
    }

    // Add audio player if audio URL is available and audio is enabled
    if (response.audio_url && audioEnabled) {
        const audioPlayer = createAudioPlayer(response.audio_url);
        contentDiv.appendChild(audioPlayer);
    }

    // Add action buttons for action plans
    if (response.action_plan) {
        const actionsDiv = createActionButtons(response.action_plan);
        contentDiv.appendChild(actionsDiv);
    }
    
    const timeDiv = document.createElement('div');
    timeDiv.className = 'message-time';
    timeDiv.textContent = new Date().toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    contentDiv.appendChild(timeDiv);
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();

    // Store in conversation history
    conversationHistory.push({
        timestamp: new Date(),
        type: 'assistant',
        response: response
    });
}

// Create action plan HTML - User-friendly version
function createActionPlan(actionPlan) {
    const planDiv = document.createElement('div');
    planDiv.className = 'action-plan';
    
    // Friendly header with icon
    const headerDiv = document.createElement('div');
    headerDiv.className = 'action-plan-header';
    headerDiv.innerHTML = `
        <div class="plan-header-content">
            <span class="plan-emoji">${getDomainIcon(actionPlan.domain)}</span>
            <div class="plan-header-text">
                <h3>Here's Your Action Plan</h3>
                <p>Follow these simple steps</p>
            </div>
        </div>
    `;
    planDiv.appendChild(headerDiv);
    
    // Steps in a clean, numbered list
    if (actionPlan.steps && actionPlan.steps.length > 0) {
        const stepsContainer = document.createElement('div');
        stepsContainer.className = 'steps-container';
        
        actionPlan.steps.forEach((step, index) => {
            const stepCard = document.createElement('div');
            stepCard.className = 'step-card';
            stepCard.innerHTML = `
                <div class="step-number">${index + 1}</div>
                <div class="step-text">
                    <div class="step-title">${step.action}</div>
                    ${step.details ? `<div class="step-subtitle">${step.details}</div>` : ''}
                </div>
            `;
            stepsContainer.appendChild(stepCard);
        });
        
        planDiv.appendChild(stepsContainer);
    }
    
    // Documents in a compact box
    if (actionPlan.documents_required && actionPlan.documents_required.length > 0) {
        const docsBox = document.createElement('div');
        docsBox.className = 'info-box documents-box';
        docsBox.innerHTML = `
            <div class="info-box-header">
                <span class="info-icon">📄</span>
                <span class="info-title">Documents You'll Need</span>
            </div>
            <div class="info-box-list">
                ${actionPlan.documents_required.map(doc => `
                    <div class="info-item">✓ ${doc}</div>
                `).join('')}
            </div>
        `;
        planDiv.appendChild(docsBox);
    }
    
    // Resources in a compact box
    if (actionPlan.resources && actionPlan.resources.length > 0) {
        const resourcesBox = document.createElement('div');
        resourcesBox.className = 'info-box resources-box';
        resourcesBox.innerHTML = `
            <div class="info-box-header">
                <span class="info-icon">📞</span>
                <span class="info-title">Contact Information</span>
            </div>
            <div class="info-box-list">
                ${actionPlan.resources.map(resource => `
                    <div class="info-item">
                        <strong>${resource.name}</strong>
                        <span>${resource.contact}</span>
                    </div>
                `).join('')}
            </div>
        `;
        planDiv.appendChild(resourcesBox);
    }
    
    // Risk alerts - NEW FEATURE
    if (actionPlan.risk_alerts && actionPlan.risk_alerts.length > 0) {
        const riskBox = document.createElement('div');
        riskBox.className = 'risk-alerts';
        riskBox.innerHTML = `
            <div class="risk-alerts-header">
                <span>⚠️</span>
                <span>Important Warnings</span>
            </div>
            ${actionPlan.risk_alerts.map(alert => `
                <div class="risk-alert-item">
                    <span>⚠️</span>
                    <span>${alert}</span>
                </div>
            `).join('')}
        `;
        planDiv.appendChild(riskBox);
    }
    
    // Estimated time - NEW FEATURE
    if (actionPlan.estimated_time) {
        const timeEstimate = document.createElement('div');
        timeEstimate.className = 'time-estimate';
        timeEstimate.innerHTML = `
            <span>⏰</span>
            <span>Estimated time: ${actionPlan.estimated_time}</span>
        `;
        planDiv.appendChild(timeEstimate);
    }
    
    return planDiv;
}



// Get domain icon
function getDomainIcon(domain) {
    const icons = {
        'agriculture': '🌾',
        'health': '🏥',
        'healthcare': '🏥',
        'government_schemes': '🏛️',
        'financial': '💰',
        'finance': '💰',
        'education': '🎓',
        'legal': '⚖️',
        'employment': '💼',
        'housing': '🏠'
    };
    return icons[domain?.toLowerCase()] || '📋';
}

// Add loading indicator
function addLoadingIndicator() {
    const loadingId = `loading-${Date.now()}`;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';
    messageDiv.id = loadingId;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = '🤖';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'loading';
    loadingDiv.innerHTML = `
        <span>Thinking</span>
        <div class="loading-dots">
            <div class="loading-dot"></div>
            <div class="loading-dot"></div>
            <div class="loading-dot"></div>
        </div>
    `;
    
    contentDiv.appendChild(loadingDiv);
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
    
    return loadingId;
}

// Remove loading indicator
function removeLoadingIndicator(loadingId) {
    const loadingElement = document.getElementById(loadingId);
    if (loadingElement) {
        loadingElement.remove();
    }
}

// Set loading state
function setLoading(loading) {
    isLoading = loading;
    messageInput.disabled = loading;
    sendBtn.disabled = loading;
}

// Scroll to bottom of chat
function scrollToBottom() {
    setTimeout(() => {
        chatMessages.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }, 100);
}

// Utility: Format time
function formatTime(date) {
    return date.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
}

// Create audio player
function createAudioPlayer(audioUrl) {
    const audioDiv = document.createElement('div');
    audioDiv.className = 'audio-player';
    
    const audioElement = document.createElement('audio');
    audioElement.controls = true;
    // Ensure full URL
    audioElement.src = audioUrl.startsWith('http') ? audioUrl : `${API_BASE_URL}${audioUrl}`;
    audioElement.className = 'audio-controls';
    audioElement.preload = 'metadata';
    
    // Auto-play if enabled in settings
    if (userSettings.autoPlayAudio) {
        audioElement.autoplay = true;
    }
    
    // Adjust playback rate if slow speech is enabled
    if (userSettings.slowSpeech) {
        audioElement.playbackRate = 0.75;
    }
    
    const audioLabel = document.createElement('div');
    audioLabel.className = 'audio-label';
    audioLabel.innerHTML = '🔊 <span>Listen to this response</span>';
    
    audioDiv.appendChild(audioLabel);
    audioDiv.appendChild(audioElement);
    
    return audioDiv;
}



// Create action buttons
function createActionButtons(actionPlan) {
    const buttonsDiv = document.createElement('div');
    buttonsDiv.className = 'action-buttons';
    
    // Download as text button
    const downloadBtn = document.createElement('button');
    downloadBtn.className = 'action-btn';
    downloadBtn.innerHTML = '💾 Download Plan';
    downloadBtn.onclick = () => downloadActionPlan(actionPlan);
    
    // Share button
    const shareBtn = document.createElement('button');
    shareBtn.className = 'action-btn';
    shareBtn.innerHTML = '📤 Share';
    shareBtn.onclick = () => shareActionPlan(actionPlan);
    
    // Simple view button (for low bandwidth)
    const simpleBtn = document.createElement('button');
    simpleBtn.className = 'action-btn';
    simpleBtn.innerHTML = '📄 Simple View';
    simpleBtn.onclick = () => showSimpleInfographic(actionPlan);
    
    buttonsDiv.appendChild(downloadBtn);
    buttonsDiv.appendChild(shareBtn);
    buttonsDiv.appendChild(simpleBtn);
    
    return buttonsDiv;
}

// Download action plan
function downloadActionPlan(actionPlan) {
    let content = `SahaayAI Action Plan\n`;
    content += `===================\n\n`;
    content += `Domain: ${actionPlan.domain}\n`;
    content += `Date: ${new Date().toLocaleDateString()}\n\n`;
    
    if (actionPlan.summary) {
        content += `Summary:\n${actionPlan.summary}\n\n`;
    }
    
    if (actionPlan.immediate_actions && actionPlan.immediate_actions.length > 0) {
        content += `Immediate Actions:\n`;
        actionPlan.immediate_actions.forEach((action, i) => {
            content += `${i + 1}. ${action}\n`;
        });
        content += `\n`;
    }
    
    if (actionPlan.steps && actionPlan.steps.length > 0) {
        content += `Detailed Steps:\n`;
        actionPlan.steps.forEach((step) => {
            content += `\nStep ${step.step_number}: ${step.action}\n`;
            if (step.details) {
                content += `   ${step.details}\n`;
            }
        });
        content += `\n`;
    }
    
    if (actionPlan.documents_required && actionPlan.documents_required.length > 0) {
        content += `Documents Required:\n`;
        actionPlan.documents_required.forEach(doc => {
            content += `• ${doc}\n`;
        });
        content += `\n`;
    }
    
    if (actionPlan.resources && actionPlan.resources.length > 0) {
        content += `Resources:\n`;
        actionPlan.resources.forEach(resource => {
            content += `• ${resource.name}: ${resource.contact}\n`;
        });
    }
    
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `sahaayai-action-plan-${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Share action plan
function shareActionPlan(actionPlan) {
    const shareText = `SahaayAI Action Plan\n\n${actionPlan.summary || 'Check out this action plan from SahaayAI'}`;
    
    if (navigator.share) {
        navigator.share({
            title: 'SahaayAI Action Plan',
            text: shareText,
            url: window.location.href
        }).then(() => {
            console.log('Shared successfully');
        }).catch((error) => {
            console.log('Error sharing:', error);
            fallbackShare(shareText);
        });
    } else {
        fallbackShare(shareText);
    }
}

// Fallback share method
function fallbackShare(text) {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
    
    // Show notification
    alert('Action plan copied to clipboard!');
}

// Show simple infographic
function showSimpleInfographic(actionPlan) {
    const modal = document.createElement('div');
    modal.className = 'modal active';
    
    const modalContent = document.createElement('div');
    modalContent.className = 'modal-content';
    
    const modalHeader = document.createElement('div');
    modalHeader.className = 'modal-header';
    modalHeader.innerHTML = `
        <h2>Simple View - ${actionPlan.domain}</h2>
        <button class="modal-close">&times;</button>
    `;
    
    const modalBody = document.createElement('div');
    modalBody.className = 'modal-body';
    
    // Create simple text infographic
    let infographic = `╔════════════════════════════════════╗\n`;
    infographic += `║  ${actionPlan.domain.toUpperCase()}  ║\n`;
    infographic += `╚════════════════════════════════════╝\n\n`;
    
    if (actionPlan.summary) {
        infographic += `${actionPlan.summary}\n\n`;
    }
    
    infographic += `┌─ STEPS TO FOLLOW ─┐\n`;
    if (actionPlan.steps) {
        actionPlan.steps.forEach((step, i) => {
            infographic += `\n${i + 1}. ${step.action}\n`;
            if (step.details) {
                infographic += `   └─ ${step.details}\n`;
            }
        });
    }
    
    if (actionPlan.documents_required && actionPlan.documents_required.length > 0) {
        infographic += `\n\n┌─ DOCUMENTS NEEDED ─┐\n`;
        actionPlan.documents_required.forEach(doc => {
            infographic += `  • ${doc}\n`;
        });
    }
    
    const preElement = document.createElement('pre');
    preElement.className = 'simple-infographic';
    preElement.textContent = infographic;
    
    modalBody.appendChild(preElement);
    modalContent.appendChild(modalHeader);
    modalContent.appendChild(modalBody);
    modal.appendChild(modalContent);
    document.body.appendChild(modal);
    
    // Close handlers
    const closeBtn = modalHeader.querySelector('.modal-close');
    closeBtn.onclick = () => {
        document.body.removeChild(modal);
    };
    
    modal.onclick = (e) => {
        if (e.target === modal) {
            document.body.removeChild(modal);
        }
    };
}

// Show conversation history
function showConversationHistory() {
    const historyContent = document.getElementById('historyContent');
    
    if (conversationHistory.length === 0) {
        historyContent.innerHTML = `
            <div class="empty-history">
                <div class="empty-icon">💬</div>
                <p>No conversation history yet.</p>
                <p class="empty-subtitle">Start chatting to build your history!</p>
            </div>
        `;
        return;
    }
    
    historyContent.innerHTML = '';
    
    conversationHistory.forEach((item, index) => {
        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';
        
        const timestamp = document.createElement('div');
        timestamp.className = 'history-timestamp';
        timestamp.textContent = item.timestamp.toLocaleString();
        
        const content = document.createElement('div');
        content.className = 'history-content-text';
        
        if (item.type === 'user') {
            content.innerHTML = `<strong>You:</strong> ${item.message}`;
        } else {
            const summary = item.response.action_plan?.summary || item.response.text || 'Response';
            content.innerHTML = `<strong>SahaayAI:</strong> ${summary.substring(0, 150)}${summary.length > 150 ? '...' : ''}`;
        }
        
        historyItem.appendChild(timestamp);
        historyItem.appendChild(content);
        historyContent.appendChild(historyItem);
    });
}

// Load user settings from localStorage
function loadSettings() {
    const saved = localStorage.getItem('sahaayai_settings');
    if (saved) {
        userSettings = JSON.parse(saved);
    }
}

// Populate settings modal with current values
function populateSettings() {
    document.getElementById('userDistrict').value = userSettings.district;
    document.getElementById('userState').value = userSettings.state;
    document.querySelector(`input[name="literacyLevel"][value="${userSettings.literacyLevel}"]`).checked = true;
    document.getElementById('autoPlayAudio').checked = userSettings.autoPlayAudio;
    document.getElementById('slowSpeech').checked = userSettings.slowSpeech;
}

// Save settings
function saveSettings() {
    userSettings.district = document.getElementById('userDistrict').value.trim();
    userSettings.state = document.getElementById('userState').value.trim();
    userSettings.literacyLevel = document.querySelector('input[name="literacyLevel"]:checked').value;
    userSettings.autoPlayAudio = document.getElementById('autoPlayAudio').checked;
    userSettings.slowSpeech = document.getElementById('slowSpeech').checked;

    localStorage.setItem('sahaayai_settings', JSON.stringify(userSettings));
    
    settingsModal.style.display = 'none';
    
    // Show success message
    addMessage('✅ Settings saved successfully!', 'assistant');
}

// Reset settings to default
function resetSettings() {
    userSettings = {
        district: '',
        state: '',
        literacyLevel: 'medium',
        autoPlayAudio: false,
        slowSpeech: false
    };
    
    localStorage.removeItem('sahaayai_settings');
    populateSettings();
    
    addMessage('🔄 Settings reset to default', 'assistant');
}

// Load knowledge base schemes from backend
async function loadKnowledgeBase() {
    try {
        // For now, use hardcoded schemes
        // In production, this would fetch from backend: /api/v1/schemes
        knowledgeBaseSchemes = [
            {
                id: 'pmjay',
                name: 'Pradhan Mantri Jan Arogya Yojana (Ayushman Bharat)',
                domain: 'health',
                description: 'Free health insurance coverage of up to ₹5 lakh per family per year for secondary and tertiary care hospitalization',
                helpline: '14555',
                website: 'https://pmjay.gov.in'
            },
            {
                id: 'pmkisan',
                name: 'PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)',
                domain: 'agriculture',
                description: 'Direct income support of ₹6,000 per year to farmer families in three equal installments',
                helpline: '155261 / 1800115526',
                website: 'https://pmkisan.gov.in'
            },
            {
                id: 'pmjdy',
                name: 'Pradhan Mantri Jan Dhan Yojana',
                domain: 'finance',
                description: 'Financial inclusion program for free bank accounts with RuPay debit card and insurance benefits',
                helpline: '1800110001 / 1800180001',
                website: 'https://pmjdy.gov.in'
            },
            {
                id: 'ujjwala',
                name: 'Pradhan Mantri Ujjwala Yojana',
                domain: 'government_schemes',
                description: 'Free LPG connections to women from BPL households',
                helpline: '1906',
                website: 'https://pmuy.gov.in'
            },
            {
                id: 'scholarship',
                name: 'National Scholarship Portal',
                domain: 'education',
                description: 'Various scholarships for students from SC/ST/OBC/Minority communities',
                helpline: '0120-6619540',
                website: 'https://scholarships.gov.in'
            }
        ];
    } catch (error) {
        console.error('Error loading knowledge base:', error);
    }
}

// Display schemes in modal
function displaySchemes(schemes) {
    const schemeResults = document.getElementById('schemeResults');
    
    if (schemes.length === 0) {
        schemeResults.innerHTML = `
            <div class="no-results">
                <div class="no-results-icon">🔍</div>
                <div class="no-results-text">No schemes found</div>
                <p>Try adjusting your search or filter</p>
            </div>
        `;
        return;
    }
    
    schemeResults.innerHTML = '';
    
    schemes.forEach(scheme => {
        const schemeCard = document.createElement('div');
        schemeCard.className = 'scheme-card';
        schemeCard.innerHTML = `
            <div class="scheme-card-header">
                <div class="scheme-icon">${getDomainIcon(scheme.domain)}</div>
                <div class="scheme-info">
                    <div class="scheme-name">${scheme.name}</div>
                    <span class="scheme-domain">${scheme.domain}</span>
                </div>
            </div>
            <div class="scheme-description">${scheme.description}</div>
            <div class="scheme-meta">
                ${scheme.helpline ? `<div class="scheme-meta-item">📞 ${scheme.helpline}</div>` : ''}
                ${scheme.website ? `<div class="scheme-meta-item">🌐 <a href="${scheme.website}" target="_blank">Visit Website</a></div>` : ''}
            </div>
        `;
        
        schemeCard.addEventListener('click', () => {
            schemeModal.style.display = 'none';
            messageInput.value = `Tell me more about ${scheme.name}`;
            handleSendMessage();
        });
        
        schemeResults.appendChild(schemeCard);
    });
}

// Search schemes
function searchSchemes() {
    const query = document.getElementById('schemeSearch').value.trim().toLowerCase();
    
    if (!query) {
        displaySchemes(knowledgeBaseSchemes);
        return;
    }
    
    const filtered = knowledgeBaseSchemes.filter(scheme => 
        scheme.name.toLowerCase().includes(query) ||
        scheme.description.toLowerCase().includes(query) ||
        scheme.domain.toLowerCase().includes(query)
    );
    
    displaySchemes(filtered);
}

// Filter schemes by domain
function filterSchemesByDomain(domain) {
    if (domain === 'all') {
        displaySchemes(knowledgeBaseSchemes);
        return;
    }
    
    const filtered = knowledgeBaseSchemes.filter(scheme => scheme.domain === domain);
    displaySchemes(filtered);
}

// Go back to home/welcome screen
function goToHome() {
    // Hide chat section, show welcome section
    chatSection.style.display = 'none';
    welcomeSection.style.display = 'block';
    homeBtn.style.display = 'none';
    
    // Optional: Clear chat messages for a fresh start
    // Uncomment the next line if you want to clear chat history when going home
    // chatMessages.innerHTML = '';
    
    // Clear input
    messageInput.value = '';
    
    // Reset loading state
    setLoading(false);
}

// Validate message content - Guardrails
function validateMessageContent(message) {
    const lowerMessage = message.toLowerCase();
    
    // 1. Check message length
    if (message.length < 3) {
        return {
            isValid: false,
            message: "Hi there! 👋\n\nYour message seems a bit short. Could you please describe your question in a little more detail? I'm here to help!"
        };
    }
    
    if (message.length > 5000) {
        return {
            isValid: false,
            message: "Hi! 👋\n\nYour message is quite long. Could you please try to keep it under 5000 characters? Feel free to break it into smaller questions if needed!"
        };
    }
    
    // 2. Block spam patterns
    const spamPatterns = [
        /(.)\1{10,}/i, // Repeated characters (e.g., "aaaaaaaaaa")
        /^[^a-zA-Z0-9\u0900-\u097F\u0980-\u09FF\u0A00-\u0A7F\u0A80-\u0AFF\u0B00-\u0B7F\u0C00-\u0C7F\u0D00-\u0D7F\u0600-\u06FF]+$/i, // Only special characters
    ];
    
    for (const pattern of spamPatterns) {
        if (pattern.test(message)) {
            return {
                isValid: false,
                message: "Hmm... 🤔\n\nI couldn't understand your message. Could you please write a clear question? I'm here to help with government services and essential information!"
            };
        }
    }
    
    // 3. Inappropriate content keywords
    const inappropriateKeywords = [
        'porn', 'xxx', 'sex', 'nude', 'naked',
        'hack', 'crack', 'pirate', 'torrent',
        'drug', 'cocaine', 'heroin', 'marijuana',
        'weapon', 'gun', 'bomb', 'explosive',
        'suicide', 'kill yourself',
        'scam', 'fraud scheme', 'money laundering',
        'casino', 'gambling', 'betting'
    ];
    
    for (const keyword of inappropriateKeywords) {
        if (lowerMessage.includes(keyword)) {
            return {
                isValid: false,
                message: "I appreciate you reaching out! 😊\n\nHowever, I'm specifically designed to help with essential services like:\n\n🏥 Healthcare and medical support\n🌾 Agriculture and farming assistance\n💰 Banking and financial services\n🏛️ Government schemes and welfare\n📚 Education and scholarships\n📋 Legal documentation help\n\nHow can I assist you with any of these topics today?"
            };
        }
    }
    
    // 4. Off-topic patterns (entertainment, unrelated topics)
    const offTopicPatterns = [
        // Entertainment
        /\b(movie|film|cinema|song|music|singer|actor|actress|celebrity|bollywood|hollywood)\b/i,
        /\b(game|video game|gaming|xbox|playstation|pubg|fortnite|minecraft)\b/i,
        /\b(netflix|amazon prime|hotstar|youtube|tiktok|instagram|facebook|twitter|snapchat|whatsapp)\b/i,
        /\b(tv show|series|episode|season|anime|cartoon)\b/i,
        // Sports
        /\b(cricket|football|soccer|hockey|tennis|basketball|badminton|ipl|world cup)\b/i,
        /\b(match|player|team|tournament|score|champion|league)\b/i,
        // Food & Dining
        /\b(recipe|cook|cooking|restaurant|cafe|pizza|burger|biryani|chai|coffee)\b/i,
        /\b(food delivery|swiggy|zomato|uber eats|dominos|mcdonalds|kfc)\b/i,
        // Shopping & E-commerce
        /\b(shopping|shop|buy|amazon|flipkart|myntra|ajio|meesho)\b/i,
        /\b(fashion|clothes|dress|shoes|jewelry|makeup|cosmetic)\b/i,
        /\b(mobile phone|smartphone|iphone|samsung|laptop|headphone|gadget)\b/i,
        // Travel & Tourism
        /\b(vacation|holiday|tour|travel|hotel|resort|flight|ticket|booking)\b/i,
        /\b(tourist|destination|beach|mountain|trip)\b/i,
        // Technology (general consumer tech, not govt services)
        /\b(android app|ios app|download app|mobile game|whatsapp status)\b/i,
        // Relationships & Personal
        /\b(boyfriend|girlfriend|relationship|dating|love|marriage proposal|crush)\b/i,
        // Astrology & Superstition
        /\b(horoscope|astrology|zodiac|luck|fortune|kundli|vastu)\b/i,
    ];
    
    for (const pattern of offTopicPatterns) {
        if (pattern.test(lowerMessage)) {
            return {
                isValid: false,
                message: "Thanks for your question! 😊\n\nI noticed this might be about entertainment, shopping, or general topics. While I'd love to chat about everything, I'm specially trained to help with:\n\n🏥 Healthcare - Finding doctors, getting insurance, medical schemes\n🌾 Agriculture - Crop advice, farming loans, subsidies\n💰 Finance - Opening bank accounts, getting loans, financial planning\n🏛️ Government Schemes - PM-JAY, PM-KISAN, scholarships, and more\n📚 Education - School admission, scholarships, training programs\n🌦️ Climate & Disasters - Weather alerts, emergency support\n\nWhat can I help you with from these areas?"
            };
        }
    }
    
    // 5. Check if message is relevant to our domains
    const domainSpecificKeywords = [
        // Health
        'health', 'hospital', 'doctor', 'medical', 'medicine', 'disease', 'illness', 'treatment',
        'insurance', 'ayushman', 'clinic', 'surgery', 'patient', 'healthcare', 'covid',
        // Agriculture
        'farm', 'crop', 'seed', 'fertilizer', 'agriculture', 'kisan', 'irrigation', 'harvest',
        'soil', 'pesticide', 'tractor', 'land', 'cultivation', 'organic', 'farmer',
        // Finance
        'bank', 'loan', 'money', 'finance', 'saving', 'account', 'credit', 'debit',
        'payment', 'insurance', 'investment', 'pension', 'subsidy', 'mudra', 'financial',
        // Government schemes
        'scheme', 'yojana', 'government', 'welfare', 'benefit', 'eligibility',
        'registration', 'certificate', 'document', 'aadhar', 'ration', 'pension',
        'subsidy', 'pradhan mantri', 'ayushman', 'ujjwala', 'awas',
        // Education
        'education', 'school', 'college', 'scholarship', 'student', 'study', 'exam',
        'degree', 'course', 'training', 'skill', 'learning', 'admission', 'fees',
        // Legal/Documentation
        'legal', 'law', 'court', 'certificate', 'license', 'permit',
        'passport', 'voter', 'pan', 'rights', 'complaint', 'ration card',
        // Climate
        'weather', 'rain', 'flood', 'drought', 'disaster', 'climate', 'cyclone',
        'emergency', 'relief', 'alert'
    ];
    
    // Generic words that should NOT count as relevant on their own
    const genericWords = ['how', 'what', 'where', 'when', 'why', 'help', 'need', 'want', 
                          'apply', 'get', 'find', 'information', 'about', 'tell', 'explain',
                          'please', 'can', 'you', 'me', 'my', 'i', 'is', 'are', 'the'];
    
    // Check if message contains at least one domain-specific keyword (not just generic words)
    const hasDomainContent = domainSpecificKeywords.some(keyword => 
        lowerMessage.includes(keyword)
    );
    
    // If message has no domain-specific content, provide guidance
    if (!hasDomainContent) {
        return {
            isValid: false,
            message: "Hello! 👋 I'm SahaayAI, your friendly assistant for essential services.\n\nI'm here to make your life easier by helping with:\n\n🏥 Healthcare - \"How do I get Ayushman Bharat card?\"\n🌾 Agriculture - \"What loans are available for farmers?\"\n💰 Finance - \"How can I open a Jan Dhan account?\"\n🏛️ Government Schemes - \"Am I eligible for PM-KISAN?\"\n📚 Education - \"What scholarships are available for students?\"\n🌦️ Climate Support - \"How to get flood relief assistance?\"\n\nTry asking me something like the examples above, and I'll do my best to help! 😊"
        };
    }
    
    // Message passed all checks
    return {
        isValid: true,
        message: ""
    };
}

// Format guardrail message with proper styling
function formatGuardrailMessage(text) {
    const container = document.createElement('div');
    container.className = 'guardrail-message';
    
    // Split message into lines
    const lines = text.split('\n');
    
    lines.forEach(line => {
        const trimmedLine = line.trim();
        
        if (!trimmedLine) {
            // Empty line - add spacing
            const spacer = document.createElement('div');
            spacer.style.height = '0.5rem';
            container.appendChild(spacer);
            return;
        }
        
        // Remove all markdown formatting
        const cleanLine = trimmedLine.replace(/\*\*/g, '');
        
        // Check if it's a heading (originally had ** on both ends)
        if (trimmedLine.startsWith('**') && trimmedLine.includes('**:')) {
            const heading = document.createElement('div');
            heading.className = 'guardrail-heading';
            heading.textContent = cleanLine;
            container.appendChild(heading);
        }
        // Check if it's a bullet point
        else if (cleanLine.startsWith('•')) {
            const bullet = document.createElement('div');
            bullet.className = 'guardrail-bullet';
            const bulletText = cleanLine.substring(2).trim();
            bullet.innerHTML = `<span class="bullet-icon">•</span> <span>${bulletText}</span>`;
            container.appendChild(bullet);
        }
        // Check if it's an emoji line (domain categories)
        else if (/^[🏥🌾💰🏛️📚🌦️⚠️🤔👋]/.test(cleanLine)) {
            const category = document.createElement('div');
            category.className = 'guardrail-category';
            category.textContent = cleanLine;
            container.appendChild(category);
        }
        // Regular text
        else {
            const para = document.createElement('div');
            para.className = 'guardrail-text';
            para.textContent = cleanLine;
            container.appendChild(para);
        }
    });
    
    return container;
}
