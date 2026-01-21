// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// State Management
let isConnected = false;
let scenesGenerated = 0;
let actionsTaken = 0;
let currentStoryContext = ''; // Track the current story for continuity
let startingSceneGenerated = false; // Track if starting scene has been generated

// DOM Elements
const connectBtn = document.getElementById('connect-btn');
const statusIndicator = document.getElementById('status-indicator');
const statusText = document.getElementById('status-text');
const storyDisplay = document.getElementById('story-display');
const choiceButtons = document.querySelectorAll('.choice-btn');
const customActionInput = document.getElementById('custom-action-input');
const submitActionBtn = document.getElementById('submit-action-btn');
const scenePromptInput = document.getElementById('scene-prompt-input');
const includeDiceCheckbox = document.getElementById('include-dice-checkbox');
const generateSceneBtn = document.getElementById('generate-scene-btn');
const diceHistory = document.getElementById('dice-history');
const scenesCount = document.getElementById('scenes-count');
const actionsCount = document.getElementById('actions-count');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    checkServerConnection();
});

// Event Listeners
function setupEventListeners() {
    connectBtn.addEventListener('click', handleConnect);
    submitActionBtn.addEventListener('click', handleCustomAction);
    generateSceneBtn.addEventListener('click', handleGenerateScene);
    
    // Enter key support
    customActionInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !submitActionBtn.disabled) {
            handleCustomAction();
        }
    });
    
    scenePromptInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !generateSceneBtn.disabled) {
            handleGenerateScene();
        }
    });
    
    // Choice button listeners
    choiceButtons.forEach((btn, index) => {
        btn.addEventListener('click', () => handleChoice(index + 1));
    });
}

// Connection Management
async function checkServerConnection() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            const wasConnected = isConnected;
            updateConnectionStatus(true);
            
            // Only show connection message and generate starting scene on first connection
            if (!wasConnected) {
                addToStory('✅ Connected to game server', 'system');
                enableGameControls();
                
                // Auto-generate starting scene only once on initial connection
                if (!startingSceneGenerated) {
                    await generateStartingScene();
                }
            }
            // If already connected, silently maintain connection (no action needed)
        } else {
            const wasConnected = isConnected;
            updateConnectionStatus(false);
            // Only show error message if we were previously connected
            if (wasConnected) {
                addToStory('❌ Error: Game server is not responding properly', 'system');
            }
        }
    } catch (error) {
        const wasConnected = isConnected;
        updateConnectionStatus(false);
        // Only show error message if we were previously connected
        if (wasConnected) {
            addToStory(`❌ Error: Cannot reach game server at ${API_BASE_URL}\n\nMake sure the FastAPI server is running.`, 'system');
        }
    }
}

async function handleConnect() {
    try {
        connectBtn.disabled = true;
        connectBtn.textContent = 'Connecting...';
        
        const response = await fetch(`${API_BASE_URL}/health`);
        
        if (response.ok) {
            updateConnectionStatus(true);
            enableGameControls();
            addToStory('Connected to AI Game Master server! Ready to begin your adventure.', 'system');
            
            // Only generate starting scene if it hasn't been generated yet
            if (!startingSceneGenerated) {
                await generateStartingScene();
            } else {
                addToStory('Game session resumed. Continue your adventure!', 'system');
            }
        } else {
            throw new Error('Server not responding');
        }
    } catch (error) {
        updateConnectionStatus(false);
        alert(`Failed to connect to server: ${error.message}\n\nMake sure the FastAPI server is running on ${API_BASE_URL}`);
    } finally {
        connectBtn.disabled = false;
        connectBtn.textContent = isConnected ? 'Reconnect' : 'Connect to Server';
    }
}

function updateConnectionStatus(connected) {
    isConnected = connected;
    
    if (connected) {
        statusIndicator.className = 'status-indicator status-online';
        statusText.textContent = 'Connected';
        connectBtn.textContent = 'Reconnect';
    } else {
        statusIndicator.className = 'status-indicator status-offline';
        statusText.textContent = 'Disconnected';
        connectBtn.textContent = 'Connect to Server';
        disableGameControls();
    }
}

function enableGameControls() {
    choiceButtons.forEach(btn => btn.disabled = false);
    customActionInput.disabled = false;
    submitActionBtn.disabled = false;
    scenePromptInput.disabled = false;
    includeDiceCheckbox.disabled = false;
    generateSceneBtn.disabled = false;
}

function disableGameControls() {
    choiceButtons.forEach(btn => btn.disabled = true);
    customActionInput.disabled = true;
    submitActionBtn.disabled = true;
    scenePromptInput.disabled = true;
    includeDiceCheckbox.disabled = true;
    generateSceneBtn.disabled = true;
}

// Story Display
function addToStory(text, type = 'game') {
    const p = document.createElement('p');
    p.className = type;
    
    if (type === 'system') {
        p.style.color = '#667eea';
        p.style.fontWeight = 'bold';
    } else if (type === 'player') {
        p.style.color = '#764ba2';
        p.style.fontWeight = '500';
    }
    
    p.textContent = text;
    storyDisplay.appendChild(p);
    storyDisplay.scrollTop = storyDisplay.scrollHeight;
    
    // Remove welcome message if present
    const welcomeMsg = storyDisplay.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }
}

// Choice Handling
async function handleChoice(choiceNumber) {
    if (!isConnected) return;
    
    const choiceText = choiceButtons[choiceNumber - 1].textContent;
    
    // Don't process if button is disabled or shows placeholder text
    if (choiceText.startsWith('Choice ') || !choiceText.trim()) {
        return;
    }
    
    addToStory(`You choose: ${choiceText}`, 'player');
    actionsTaken++;
    updateStats();
    
    // Disable buttons while processing
    choiceButtons.forEach(btn => btn.disabled = true);
    
    try {
        // Build a continuation prompt that maintains story context
        const continuationPrompt = buildContinuationPrompt(choiceText);
        // Generate a follow-up scene that continues the current story
        await generateSceneFromPrompt(continuationPrompt, false, true);
    } catch (error) {
        addToStory(`Error: ${error.message}`, 'system');
    } finally {
        // Buttons will be re-enabled after scene generation updates them
    }
}

// Custom Action Handling
async function handleCustomAction() {
    if (!isConnected) return;
    
    const action = customActionInput.value.trim();
    if (!action) return;
    
    addToStory(`You: ${action}`, 'player');
    customActionInput.value = '';
    actionsTaken++;
    updateStats();
    
    // Disable input while processing
    submitActionBtn.disabled = true;
    customActionInput.disabled = true;
    
    try {
        // Build a continuation prompt that maintains story context
        const continuationPrompt = buildContinuationPrompt(action);
        // Generate a scene that continues the current story
        await generateSceneFromPrompt(continuationPrompt, false, true);
    } catch (error) {
        addToStory(`Error: ${error.message}`, 'system');
    } finally {
        submitActionBtn.disabled = false;
        customActionInput.disabled = false;
        customActionInput.focus();
    }
}

// Generate Starting Scene
async function generateStartingScene() {
    if (!isConnected || startingSceneGenerated) return;
    
    // Mark as generated to prevent multiple calls
    startingSceneGenerated = true;
    
    // Reset story context for a new adventure
    currentStoryContext = '';
    
    const startingPrompt = "a fantasy adventure beginning - the player finds themselves at the start of an epic quest in a mysterious world";
    
    addToStory('🎮 Generating your starting adventure...', 'system');
    
    try {
        await generateSceneFromPrompt(startingPrompt, false, false);
    } catch (error) {
        addToStory(`Error generating starting scene: ${error.message}`, 'system');
        console.error('Error:', error);
        // Reset flag if generation failed so user can try again
        startingSceneGenerated = false;
    }
}

// Build Continuation Prompt
function buildContinuationPrompt(playerAction) {
    // Build a prompt that continues the current story
    let prompt = `Continue the current story. The player chooses to: ${playerAction}. `;
    
    if (currentStoryContext) {
        // Include recent story context (last 500 characters to avoid token limits)
        const recentContext = currentStoryContext.slice(-500);
        prompt += `Continue from where the story left off. Recent context: ${recentContext}. `;
    }
    
    prompt += `Describe what happens next as a result of this choice, maintaining continuity with the ongoing narrative.`;
    
    return prompt;
}

// Scene Generation Helper Function
async function generateSceneFromPrompt(prompt, includeDice = false, isContinuation = false) {
    if (!isConnected) return;
    
    scenesGenerated++;
    updateStats();
    
    try {
        const response = await fetch(`${API_BASE_URL}/generate-scene`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                prompt: prompt,
                include_dice_rolls: includeDice
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to generate scene');
        }
        
        const data = await response.json();
        
        if (data.success) {
            // Display the generated scene
            addToStory(data.scene, 'game');
            
            // Update story context for continuity
            if (isContinuation) {
                // Append to existing context
                currentStoryContext += ' ' + data.scene;
            } else {
                // New story or scene - start fresh context
                currentStoryContext = data.scene;
            }
            
            // Keep context manageable (last 2000 characters)
            if (currentStoryContext.length > 2000) {
                currentStoryContext = currentStoryContext.slice(-2000);
            }
            
            // Extract and display dice rolls
            extractAndDisplayDiceRolls(data.scene);
            
            // Update choice buttons with suggested actions
            updateChoiceButtons(data.scene);
        } else {
            throw new Error('Scene generation failed');
        }
    } catch (error) {
        addToStory(`Error generating scene: ${error.message}`, 'system');
        console.error('Error:', error);
        throw error;
    }
}

// Scene Generation (Manual)
async function handleGenerateScene() {
    if (!isConnected) return;
    
    const prompt = scenePromptInput.value.trim();
    if (!prompt) {
        alert('Please enter a scene description');
        return;
    }
    
    const includeDice = includeDiceCheckbox.checked;
    
    addToStory(`Generating scene: ${prompt}`, 'system');
    
    // Disable controls while processing
    generateSceneBtn.disabled = true;
    scenePromptInput.disabled = true;
    generateSceneBtn.textContent = 'Generating...';
    
    try {
        await generateSceneFromPrompt(prompt, includeDice);
    } catch (error) {
        // Error already displayed in generateSceneFromPrompt
    } finally {
        generateSceneBtn.disabled = false;
        scenePromptInput.disabled = false;
        generateSceneBtn.textContent = 'Generate Scene';
        scenePromptInput.value = '';
        includeDiceCheckbox.checked = false;
    }
}

// Extract and Display Dice Rolls
function extractAndDisplayDiceRolls(sceneText) {
    // Pattern to match dice notation like "3d6", "1d20", "2d10+5", etc.
    const dicePattern = /(\d+d\d+(?:[+-]\d+)?)/gi;
    const rollResultsPattern = /Rolled\s+(\d+d\d+(?:[+-]\d+)?):\s*\[([^\]]+)\](?:\s*([+-]\d+))?\s*=\s*(\d+)/gi;
    
    // First, try to find formatted roll results
    let match;
    const foundRolls = [];
    
    while ((match = rollResultsPattern.exec(sceneText)) !== null) {
        const diceNotation = match[1];
        const individualRolls = match[2];
        const modifier = match[3] || '';
        const total = match[4];
        
        foundRolls.push({
            notation: diceNotation,
            rolls: individualRolls.split(',').map(r => r.trim()),
            modifier: modifier,
            total: total
        });
    }
    
    // If no formatted results found, look for dice notation mentions
    if (foundRolls.length === 0) {
        const diceMatches = sceneText.match(dicePattern);
        if (diceMatches) {
            diceMatches.forEach(notation => {
                foundRolls.push({
                    notation: notation,
                    rolls: [],
                    modifier: '',
                    total: ''
                });
            });
        }
    }
    
    // Add to dice history
    if (foundRolls.length > 0) {
        const emptyMsg = diceHistory.querySelector('.empty-message');
        if (emptyMsg) {
            emptyMsg.remove();
        }
        
        foundRolls.forEach(roll => {
            const rollItem = document.createElement('div');
            rollItem.className = 'dice-roll-item';
            
            if (roll.total) {
                // Formatted result
                const rollsText = roll.rolls.join(', ');
                rollItem.textContent = `🎲 ${roll.notation}: [${rollsText}]${roll.modifier} = ${roll.total}`;
            } else {
                // Just notation
                rollItem.textContent = `🎲 ${roll.notation}`;
            }
            
            diceHistory.insertBefore(rollItem, diceHistory.firstChild);
        });
    }
}

// Update Choice Buttons
function updateChoiceButtons(sceneText) {
    // Extract potential actions from the scene text
    // Look for sentences that suggest actions or choices
    const sentences = sceneText.split(/[.!?]/)
        .map(s => s.trim())
        .filter(s => {
            // Filter for sentences that suggest actions (contain action words or are questions)
            const actionWords = ['you can', 'you might', 'you could', 'you may', 'will you', 'do you', 'would you', 'choose', 'decide', 'option'];
            const lowerText = s.toLowerCase();
            return s.length > 15 && s.length < 200 && 
                   (actionWords.some(word => lowerText.includes(word)) || 
                    lowerText.includes('?') ||
                    lowerText.startsWith('you'));
        });
    
    // Take up to 4 action sentences, or generate generic choices if not enough
    const actions = sentences.slice(0, 4);
    
    // If we don't have enough actions, create some generic ones based on the scene
    if (actions.length < 4) {
        const genericActions = [
            'Explore further',
            'Investigate the area',
            'Take action',
            'Continue the adventure'
        ];
        
        // Fill remaining slots with generic actions
        for (let i = actions.length; i < 4; i++) {
            actions.push(genericActions[i - actions.length]);
        }
    }
    
    choiceButtons.forEach((btn, index) => {
        if (actions[index]) {
            // Set full text without truncation
            btn.textContent = actions[index].trim();
            btn.disabled = false;
            
            // Add title attribute for tooltip if text is long
            if (actions[index].length > 60) {
                btn.title = actions[index].trim();
            } else {
                btn.removeAttribute('title');
            }
        } else {
            btn.textContent = `Choice ${index + 1}`;
            btn.disabled = true;
            btn.removeAttribute('title');
        }
    });
}

// Legacy function - now uses extractAndDisplayDiceRolls
function addDiceRollToHistory(sceneText) {
    extractAndDisplayDiceRolls(sceneText);
}

// Stats Update
function updateStats() {
    scenesCount.textContent = scenesGenerated;
    actionsCount.textContent = actionsTaken;
}

// Periodic connection check
setInterval(checkServerConnection, 30000); // Check every 30 seconds
