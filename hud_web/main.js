let backend = null;
let bars = [];
const NUM_BARS = 32;
let currentState = "IDLE";
let plasmaCanvas = document.getElementById('plasma-core');
let ctx = plasmaCanvas.getContext('2d');
let time = 0;

// Setup Waveform
const waveformContainer = document.getElementById('waveform');
for (let i = 0; i < NUM_BARS; i++) {
    const bar = document.createElement('div');
    bar.className = 'bar';
    waveformContainer.appendChild(bar);
    bars.push(bar);
}

// Draw Plasma Core
function drawPlasma(amp) {
    plasmaCanvas.width = 150;
    plasmaCanvas.height = 150;
    const cx = 75, cy = 75;
    
    ctx.clearRect(0, 0, 150, 150);
    
    // Base glow
    let radius = 60 + amp * 30;
    let gradient = ctx.createRadialGradient(cx, cy, 0, cx, cy, radius);
    
    let color = getComputedStyle(document.body).getPropertyValue(
        currentState === 'SPEAKING' ? '--color-primary' : 
        currentState === 'LISTENING' ? '--color-secondary' : '--color-primary'
    ).trim();
    
    gradient.addColorStop(0, color);
    gradient.addColorStop(1, 'transparent');
    
    ctx.fillStyle = gradient;
    ctx.beginPath();
    ctx.arc(cx, cy, radius, 0, Math.PI * 2);
    ctx.fill();
}

// QWebChannel setup
if (typeof QWebChannel !== 'undefined') {
    new QWebChannel(qt.webChannelTransport, function (channel) {
        backend = channel.objects.hudBackend;
        
        // Listen for signals
        backend.audioLevelChanged.connect(function(level) {
            updateAudio(level);
        });
        
        backend.stateChanged.connect(function(state) {
            setState(state);
        });
        
        backend.colorsChanged.connect(function(primary, secondary, accent) {
            document.documentElement.style.setProperty('--color-primary', primary);
            document.documentElement.style.setProperty('--color-secondary', secondary);
            document.documentElement.style.setProperty('--color-accent', accent);
        });
        
        backend.notifyReady();
    });
}

function updateAudio(level) {
    // level is 0.0 to 1.0
    const active = level > 0.05;
    
    // Update bars
    for (let i = 0; i < NUM_BARS; i++) {
        // Create a fake spectrum shape around center
        const distFromCenter = Math.abs(i - NUM_BARS/2) / (NUM_BARS/2);
        const weight = Math.max(0, 1 - distFromCenter * distFromCenter);
        const randomFactor = 0.5 + Math.random() * 0.5;
        const barLevel = active ? (level * weight * randomFactor * 100) : 5;
        
        bars[i].style.height = `${Math.max(5, barLevel)}%`;
    }
    
    drawPlasma(level);
}

function setState(state) {
    currentState = state;
    document.body.className = '';
    
    if (state === 'SPEAKING') {
        document.body.classList.add('state-speaking');
    } else if (state === 'LISTENING') {
        document.body.classList.add('state-listening');
    } else {
        document.body.classList.add('state-idle');
    }
    
    // Redraw plasma with new color immediately
    drawPlasma(0);
}

// Initial draw
drawPlasma(0);

// Fallback animation loop
setInterval(() => {
    // If backend is not active or we want constant ambient motion
    time += 0.05;
    let baseAmp = Math.sin(time) * 0.05 + 0.05;
    // We only use the fallback ambient pulse if we're not receiving live audio
    if (currentState !== 'SPEAKING' && currentState !== 'LISTENING') {
         drawPlasma(baseAmp);
    }
}, 50);
