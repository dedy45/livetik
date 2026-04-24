#!/usr/bin/env node
const WebSocket = require('ws');

const ws = new WebSocket('ws://127.0.0.1:8765');

ws.on('open', () => {
    console.log('Connected to worker');
    const reqId = 'test-' + Date.now();
    ws.send(JSON.stringify({
        type: 'cmd',
        name: 'audio.list',
        req_id: reqId,
        params: {}
    }));
    console.log('Sent audio.list command with req_id:', reqId);
});

ws.on('message', (data) => {
    const msg = JSON.parse(data.toString());
    if (msg.type === 'cmd_result' && msg.name === 'audio.list') {
        console.log('\n=== RESULT ===');
        console.log('OK:', msg.ok);
        console.log('Clips count:', msg.result?.clips?.length || 0);
        if (msg.result?.clips?.length > 0) {
            console.log('First 3 clips:');
            msg.result.clips.slice(0, 3).forEach(c => {
                console.log(`  - ${c.id} (${c.category})`);
            });
        }
        ws.close();
        process.exit(0);
    }
});

ws.on('error', (err) => {
    console.error('WebSocket error:', err.message);
    process.exit(1);
});

setTimeout(() => {
    console.error('Timeout - no response');
    process.exit(1);
}, 5000);
