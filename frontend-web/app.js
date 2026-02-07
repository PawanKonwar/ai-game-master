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
      rollD20Btn = document.getElementById('roll-d20-btn'),
      saveGameBtn = document.getElementById('save-game-btn'),
      diceResultEl = document.getElementById('dice-result'),
      diceHistoryEl = document.getElementById('dice-history'),
      previousAdventuresEl = document.getElementById('previous-adventures'),
      scenesCount = document.getElementById('scenes-count'),
      actionsCount = document.getElementById('actions-count');

document.addEventListener('DOMContentLoaded', () => { 
    setupEventListeners(); 
    checkServerConnection();
    fetchPreviousAdventures();
});

function setupEventListeners() {
    connectBtn.onclick = handleConnect;
    submitActionBtn.onclick = handleCustomAction;
    generateSceneBtn.onclick = handleGenerateScene;
    rollD20Btn.onclick = handleRollD20;
    saveGameBtn.onclick = handleSaveGame;
    choiceButtons.forEach((btn, i) => btn.onclick = () => handleChoice(i + 1));
}

// FIX: Ensures inputs are unlocked after AI finishes
function enableControls() {
    [customActionInput, submitActionBtn, scenePromptInput, generateSceneBtn, rollD20Btn, saveGameBtn].forEach(el => el.disabled = false);
    choiceButtons.forEach(btn => btn.disabled = false);
}

function disableControls() {
    [customActionInput, submitActionBtn, scenePromptInput, generateSceneBtn, rollD20Btn, saveGameBtn].forEach(el => el.disabled = true);
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
        if (res.ok) fetchPreviousAdventures();
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

const DICE_SHAKE_MS = 650;

async function handleRollD20() {
    if (!isConnected) return;
    disableControls();
    const roll = 1 + Math.floor(Math.random() * 20);
    diceResultEl.textContent = '…';
    diceResultEl.classList.add('shake');
    await new Promise(r => setTimeout(r, DICE_SHAKE_MS));
    diceResultEl.classList.remove('shake');
    diceResultEl.textContent = roll;
    addToDiceHistory('D20', roll);
    addToStory(`> Rolled D20: ${roll}`, 'player');
    actionsTaken++;
    await sendToAI(`I rolled a ${roll} for my last action. Narrate the outcome based on this roll.`);
}

function addToDiceHistory(notation, value) {
    const empty = diceHistoryEl.querySelector('.empty-message');
    if (empty) empty.remove();
    const item = document.createElement('div');
    item.className = 'dice-roll-item';
    item.textContent = `${notation}: ${value}`;
    diceHistoryEl.appendChild(item);
    diceHistoryEl.scrollTop = diceHistoryEl.scrollHeight;
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

function getStoryLogText() {
    const paragraphs = storyDisplay.querySelectorAll('p');
    return Array.from(paragraphs).map(p => p.textContent.trim()).filter(Boolean).join('\n');
}

function setStoryFromLog(storyLog) {
    storyDisplay.innerHTML = '';
    if (!storyLog.trim()) {
        const welcome = document.createElement('p');
        welcome.className = 'welcome-message';
        welcome.textContent = 'Welcome to the AI Game Master! Click "Connect to Server" to begin your adventure.';
        storyDisplay.appendChild(welcome);
        return;
    }
    const lines = storyLog.split('\n');
    lines.forEach(line => {
        const p = document.createElement('p');
        if (line.startsWith('> ')) {
            p.className = 'player';
            p.textContent = line;
        } else if (line.startsWith('[') || /^🎮|^Error/.test(line)) {
            p.className = 'system';
            p.textContent = line;
        } else {
            p.className = 'game';
            p.innerHTML = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        }
        storyDisplay.appendChild(p);
    });
    storyDisplay.scrollTop = storyDisplay.scrollHeight;
}

async function fetchPreviousAdventures() {
    try {
        const res = await fetch(`${API_BASE_URL}/saves`);
        if (!res.ok) return;
        const data = await res.json();
        renderPreviousAdventures(data.saves || []);
    } catch {
        renderPreviousAdventures([]);
    }
}

function renderPreviousAdventures(saves) {
    const empty = previousAdventuresEl.querySelector('.empty-message');
    if (empty) empty.remove();
    previousAdventuresEl.querySelectorAll('.adventure-item').forEach(el => el.remove());
    if (saves.length === 0) {
        const msg = document.createElement('p');
        msg.className = 'empty-message';
        msg.textContent = 'No saved games';
        previousAdventuresEl.appendChild(msg);
        return;
    }
    saves.forEach(({ id, session_name, timestamp }) => {
        const item = document.createElement('button');
        item.type = 'button';
        item.className = 'adventure-item';
        item.dataset.id = String(id);
        const date = timestamp ? new Date(timestamp).toLocaleString(undefined, { dateStyle: 'short', timeStyle: 'short' }) : '';
        item.innerHTML = `<span class="adventure-name">${escapeHtml(session_name)}</span><span class="adventure-date">${escapeHtml(date)}</span>`;
        item.onclick = () => handleLoadAdventure(id);
        previousAdventuresEl.appendChild(item);
    });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

async function handleSaveGame() {
    const storyLog = getStoryLogText();
    if (!storyLog || storyLog.length < 2) {
        addToStory('Nothing to save yet. Play a bit first!', 'system');
        return;
    }
    const sessionName = prompt('Name this adventure:', 'My Adventure')?.trim() || 'My Adventure';
    saveGameBtn.disabled = true;
    saveGameBtn.textContent = 'Saving...';
    try {
        const res = await fetch(`${API_BASE_URL}/save`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_name: sessionName, story_log: storyLog }),
        });
        const data = await res.json();
        if (data.success) {
            addToStory('Game saved.', 'system');
            fetchPreviousAdventures();
        } else {
            addToStory('Failed to save.', 'system');
        }
    } catch {
        addToStory('Error saving game.', 'system');
    } finally {
        saveGameBtn.textContent = 'Save Game';
        saveGameBtn.disabled = false;
    }
}

async function handleLoadAdventure(sessionId) {
    try {
        const res = await fetch(`${API_BASE_URL}/load/${sessionId}`);
        if (!res.ok) {
            addToStory('Could not load that save.', 'system');
            return;
        }
        const data = await res.json();
        setStoryFromLog(data.story_log || '');
        addToStory(`Loaded: ${data.session_name || 'Adventure'}`, 'system');
    } catch {
        addToStory('Error loading game.', 'system');
    }
}