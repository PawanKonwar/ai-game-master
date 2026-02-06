const API_BASE_URL = 'http://localhost:8000';
let isConnected = false, scenesGenerated = 0, actionsTaken = 0, currentStoryContext = '', startingSceneGenerated = false;

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
    } catch { isConnected = false; }
}

async function handleConnect() {
    await checkServerConnection();
}

function addToStory(text, type = 'game') {
    if (!text) return;
    const p = document.createElement('p');
    p.className = type;
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
            // 1. Put choices on buttons
            updateChoiceButtons(data.scene);

            // 2. CLEANING LOGIC: Cut the text off BEFORE "Choice 1:"
            const choiceIndex = data.scene.search(/Choice \d+:/i);
            const cleanedStory = choiceIndex !== -1 
                ? data.scene.substring(0, choiceIndex).trim() 
                : data.scene.trim();

            // 3. Only show the cleaned narrative in the window
            addToStory(cleanedStory, 'game');
        }
    } catch (e) { 
        addToStory("Error contacting AI.", "system"); 
    } finally {
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
        btn.textContent = raw.length > 40 ? raw.substring(0, 37) + '...' : raw;
        btn.title = raw;
    });
}

function handleGenerateScene() {
    const val = scenePromptInput.value.trim();
    if (val) sendToAI(val);
}