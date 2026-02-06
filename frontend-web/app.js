const API_BASE_URL = 'http://localhost:8000';
let isConnected = false, scenesGenerated = 0, actionsTaken = 0, startingSceneGenerated = false;

// DOM Elements
const connectBtn = document.getElementById('connect-btn'), 
      storyDisplay = document.getElementById('story-display'),
      choiceButtons = document.querySelectorAll('.choice-btn'),
      customActionInput = document.getElementById('custom-action-input'),
      submitActionBtn = document.getElementById('submit-action-btn'),
      scenePromptInput = document.getElementById('scene-prompt-input'),
      generateSceneBtn = document.getElementById('generate-scene-btn'),
      scenesCount = document.getElementById('scenes-count'),
      actionsCount = document.getElementById('actions-count');

document.addEventListener('DOMContentLoaded', () => { 
    setupEventListeners(); 
    checkServerConnection(); 
});

function setupEventListeners() {
    connectBtn.onclick = handleConnect;
    submitActionBtn.onclick = handleCustomAction;
    generateSceneBtn.onclick = handleGenerateScene;
    choiceButtons.forEach((btn, i) => btn.onclick = () => handleChoice(i + 1));
}

// FIX: Ensures inputs are unlocked after AI finishes
function enableControls() {
    [customActionInput, submitActionBtn, scenePromptInput, generateSceneBtn].forEach(el => el.disabled = false);
    choiceButtons.forEach(btn => btn.disabled = false);
}

function disableControls() {
    [customActionInput, submitActionBtn, scenePromptInput, generateSceneBtn].forEach(el => el.disabled = true);
    choiceButtons.forEach(btn => btn.disabled = true);
}

async function checkServerConnection() {
    try {
        const res = await fetch(`${API_BASE_URL}/health`);
        if (res.ok && !isConnected) {
            isConnected = true;
            enableControls();
            if (!startingSceneGenerated) generateStartingScene();
        }
    } catch { 
        isConnected = false; 
        console.log("Waiting for server...");
    }
}

async function handleConnect() {
    connectBtn.textContent = 'Connecting...';
    await checkServerConnection();
    if(isConnected) connectBtn.textContent = 'Connected';
}

function addToStory(text, type = 'game') {
    if (!text) return;
    const p = document.createElement('p');
    p.className = type;
    // Highlight bold text from AI markdown
    p.innerHTML = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>'); 
    storyDisplay.appendChild(p);
    storyDisplay.scrollTop = storyDisplay.scrollHeight;
}

async function handleCustomAction() {
    const val = customActionInput.value.trim();
    if (!val || !isConnected) return;
    addToStory(`> ${val}`, 'player');
    customActionInput.value = '';
    actionsTaken++;
    await sendToAI(val);
}

async function handleChoice(num) {
    const btn = choiceButtons[num-1];
    const text = btn.getAttribute('title') || btn.textContent;
    if (!isConnected || text === 'Rest' || text === 'Continue') return;
    addToStory(`> ${text}`, 'player');
    actionsTaken++;
    await sendToAI(text);
}

async function generateStartingScene() {
    startingSceneGenerated = true;
    addToStory('🎮 Awakening the Game Master...', 'system');
    await sendToAI("The adventure begins.");
}

async function sendToAI(prompt) {
    scenesGenerated++;
    scenesCount.textContent = scenesGenerated;
    actionsCount.textContent = actionsTaken;
    disableControls(); 

    try {
        const res = await fetch(`${API_BASE_URL}/generate-scene`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt: prompt })
        });
        const data = await res.json();
        
        if (data.success) {
            // 1. UPDATE BUTTONS (Uses the full text)
            updateChoiceButtons(data.scene);

            // 2. CLEANING LOGIC (Removes "Choice 1..." from the main window)
            // Searches for "Choice 1" or "Choice 1:" case-insensitively
            const choiceIndex = data.scene.search(/Choice\s*1/i);
            
            const displayContent = choiceIndex !== -1 
                ? data.scene.substring(0, choiceIndex).trim() 
                : data.scene.trim();

            // 3. Only add narrative text to the story window
            addToStory(displayContent, 'game');
        }
    } catch (e) { 
        addToStory("Error contacting AI.", "system"); 
    } finally {
        // ALWAYS unlock controls even if the server fails
        enableControls();
    }
}

function updateChoiceButtons(text) {
    const choiceRegex = /Choice \d+:\s*(.*)/gi;
    let choices = [], match;
    
    while ((match = choiceRegex.exec(text)) !== null) {
        choices.push(match[1].trim());
    }

    const fallbacks = ['Explore further', 'Search area', 'Rest', 'Continue'];
    
    choiceButtons.forEach((btn, i) => {
        const raw = choices[i] || fallbacks[i];
        // Truncate text for button visual (adds ...)
        btn.textContent = raw.length > 40 ? raw.substring(0, 37) + '...' : raw;
        // Store full text in title for tooltips and game logic
        btn.title = raw;
    });
}

function handleGenerateScene() {
    const val = scenePromptInput.value.trim();
    if (val) sendToAI(val);
}