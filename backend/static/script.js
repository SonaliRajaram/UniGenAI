// =============== USER SESSION MANAGEMENT ===============
let currentUserId = null;
let currentUsername = null;
let userInitialized = false;

// Initialize user on page load
async function initializeUser() {
    try {
        const stored = localStorage.getItem("unigenai_user");
        
        if (stored) {
            const user = JSON.parse(stored);
            currentUserId = user.id;
            currentUsername = user.username;
            console.log(`✓ Loaded existing user: ${currentUsername} (ID: ${currentUserId})`);
        } else {
            // Create new user
            const username = `user_${Date.now()}`;
            console.log(`Creating new user: ${username}`);
            await createNewUser(username);
        }
        
        userInitialized = true;
        console.log(`✓ User initialization complete. ID: ${currentUserId}`);
    } catch (error) {
        console.error("✗ User initialization failed:", error);
    }
}

async function createNewUser(username) {
    try {
        const response = await fetch(`/api/user/create?username=${username}`, {
            method: "POST"
        });
        
        if (!response.ok) {
            console.error(`Failed to create user: HTTP ${response.status}`);
            throw new Error(`HTTP ${response.status}`);
        }
        
        const user = await response.json();
        currentUserId = user.id;
        currentUsername = user.username;
        
        // Store in localStorage
        localStorage.setItem("unigenai_user", JSON.stringify({
            id: user.id,
            username: user.username
        }));
        
        console.log(`✓ Created new user: ${username} (ID: ${currentUserId})`);
    } catch (error) {
        console.error("✗ Failed to create user:", error);
        throw error;
    }
}

// =============== UI AND CHAT LOGIC ===============

let selectedRole = null;
let activeAgent = null;  // currently responding agent (AUTO)
let voiceEnabled = true;

const chatBox = document.getElementById("chat-box");
const input = document.getElementById("user-input");

function selectRole(role) {
    if (!userInitialized) {
        alert("User still initializing... Please wait a moment and try again.");
        return;
    }
    
    if (!currentUserId) {
        alert("User initialization failed. Please refresh the page.");
        return;
    }
    
    selectedRole = role;
    activeAgent = role; // initial agent

    document.getElementById("role-selection").classList.add("hidden");
    chatBox.innerHTML = "";
    document.getElementById("chat-container").classList.remove("hidden");

    switchAgentUI(role);
}

function switchAgentUI(agent) {
    activeAgent = agent;

    const titles = {
        academic: "Academic Helper",
        content: "Content Creator",
        code: "Code Assistant",
        general: "General Assistant"
    };

    document.getElementById("role-title").innerText = titles[agent];

    // academic tools toggle
    document.getElementById("academic-tools")
        ?.classList.toggle("hidden", agent !== "academic");

    setTimeout(() => {
        chatBox.scrollTop = chatBox.scrollHeight;
    }, 0);
}

function resetRole() {
    location.reload();
}

/* ENTER KEY */
input.addEventListener("keydown", e => {
    if (e.key === "Enter") sendMessage();
});

/* SEND MESSAGE (STREAMING + VOICE) */
async function sendMessage() {
    const message = input.value.trim();
    if (!message) return;
    
    // Check if user is initialized
    if (!currentUserId) {
        alert("User not initialized. Please refresh the page.");
        return;
    }

    // USER BUBBLE
    const userDiv = document.createElement("div");
    userDiv.className = "message user";
    userDiv.innerText = message;
    chatBox.appendChild(userDiv);
    input.value = "";

    // AI BUBBLE
    const aiDiv = document.createElement("div");
    aiDiv.className = "message bot";
    chatBox.appendChild(aiDiv);

    let fullResponse = "";

    try {
        // Send user_id if available (otherwise backend defaults to 1)
        const url = currentUserId ? `/chat?user_id=${currentUserId}` : `/chat`;
        console.log(`Sending message with user_id=${currentUserId} to: ${url}`);
        
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Accept": "text/event-stream"
            },
            body: JSON.stringify({
                message: message,
                forced_role: selectedRole
            })
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error(`HTTP ${response.status}:`, errorText);
            aiDiv.innerText = `Error: ${response.status}`;
            return;
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const events = buffer.split("\n\n");
            buffer = events.pop();

            for (const event of events) {
                if (!event.startsWith("data: ")) continue;

                const data = JSON.parse(event.replace("data: ", ""));
                if (data.agent && data.agent !== activeAgent) {
                    switchAgentUI(data.agent);
                }

                if (data.token) {
                    aiDiv.innerHTML += data.token.replace(/\n/g, "<br>");
                    fullResponse += data.token;
                }
            }
        }

        // SPEAK AFTER FULL RESPONSE
        speak(fullResponse);
        
        // Scroll to bottom
        setTimeout(() => {
            chatBox.scrollTop = chatBox.scrollHeight;
        }, 0);
    } catch (error) {
        console.error("Send message error:", error);
        aiDiv.innerText = `Error: ${error.message}`;
    }
}

/* VOICE INPUT */
function startVoice() {
    if (!("webkitSpeechRecognition" in window)) {
        alert("Voice input not supported");
        return;
    }

    const recog = new webkitSpeechRecognition();
    recog.lang = "en-US";
    recog.start();

    recog.onresult = e => {
        input.value = e.results[0][0].transcript;
        sendMessage();
    };
}

/* VOICE OUTPUT */
function toggleVoice() {
    voiceEnabled = !voiceEnabled;
    document.getElementById("voice-toggle").innerText =
        voiceEnabled ? "🔊 Voice ON" : "🔇 Voice OFF";
    window.speechSynthesis.cancel();
}

function speak(text) {
    if (!voiceEnabled || !text.trim()) return;

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "en-US";
    utterance.rate = 1;
    utterance.pitch = 1;

    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utterance);
}

/* ACADEMIC TOOLS  */
async function uploadPDF() {
    const fileInput = document.getElementById("pdf-upload");
    if (!fileInput.files.length) return;

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    const res = await fetch("/upload-pdf", { method: "POST", body: formData });
    const data = await res.json();

    const botDiv = document.createElement("div");
    botDiv.className = "message bot";
    botDiv.innerText = data.message;
    chatBox.appendChild(botDiv);
    
    chatBox.scrollTop = chatBox.scrollHeight;
}

function togglePlanner() {
    document.getElementById("planner-box").classList.toggle("hidden");
}

function submitPlanner() {
    const date = document.getElementById("exam-date").value;
    const hours = document.getElementById("hours").value;
    input.value = `Create a study plan for my interview on ${date}. I can study ${hours} hours per day.`;
    sendMessage();
}

function startMockInterview() {
    selectedRole = "academic";
    input.value = "start mock interview";
    sendMessage();
}
