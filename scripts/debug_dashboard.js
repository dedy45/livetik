#!/usr/bin/env node
/**
 * Debug dashboard WebSocket connection and audio library state
 * 
 * This script:
 * 1. Connects to worker WebSocket
 * 2. Sends audio.list command
 * 3. Reports what worker returns
 * 4. Diagnoses the issue
 */

const WebSocket = require('ws');

const WS_URL = 'ws://127.0.0.1:8765';
const TIMEOUT_MS = 5000;

console.log('='.repeat(70));
console.log('DASHBOARD DEBUG - WebSocket Audio Library Test');
console.log('='.repeat(70));
console.log();

async function testAudioList() {
    return new Promise((resolve, reject) => {
        console.log(`Connecting to: ${WS_URL}`);
        
        const ws = new WebSocket(WS_URL);
        let responseReceived = false;
        
        const timeout = setTimeout(() => {
            if (!responseReceived) {
                ws.close();
                reject(new Error(`Timeout after ${TIMEOUT_MS}ms - no response from worker`));
            }
        }, TIMEOUT_MS);
        
        ws.on('open', () => {
            console.log('✓ Connected to worker WebSocket\n');
            
            const command = {
                type: 'cmd',
                name: 'audio.list',
                req_id: 'debug-test-' + Date.now(),
                params: {}
            };
            
            console.log('Sending command:', JSON.stringify(command, null, 2));
            ws.send(JSON.stringify(command));
        });
        
        ws.on('message', (data) => {
            try {
                const msg = JSON.parse(data.toString());
                
                // Look for cmd_result response
                if (msg.type === 'cmd_result' && msg.name === 'audio.list') {
                    responseReceived = true;
                    clearTimeout(timeout);
                    
                    console.log('\n✓ Received response from worker:');
                    console.log(`  Type: ${msg.type}`);
                    console.log(`  OK: ${msg.ok}`);
                    console.log(`  Latency: ${msg.latency_ms}ms`);
                    
                    if (msg.ok && msg.result) {
                        const clips = msg.result.clips || [];
                        console.log(`\n  Clips returned: ${clips.length}`);
                        
                        if (clips.length > 0) {
                            console.log('\n  ✓ SUCCESS! Worker has audio clips');
                            console.log('\n  First 5 clips:');
                            clips.slice(0, 5).forEach((clip, i) => {
                                console.log(`    [${i+1}] ${clip.id} (${clip.category}) - ${clip.duration_ms}ms`);
                            });
                            
                            console.log('\n  DIAGNOSIS:');
                            console.log('  - Worker loaded index.json successfully');
                            console.log('  - WebSocket communication working');
                            console.log('  - Problem is in FRONTEND (Svelte controller)');
                            console.log('\n  NEXT STEPS:');
                            console.log('  1. Check browser console for errors (F12)');
                            console.log('  2. Check Network tab for WebSocket messages');
                            console.log('  3. Verify wsStore.connected = true');
                            console.log('  4. Check if $effect() is triggering');
                            
                        } else {
                            console.log('\n  ❌ PROBLEM: Worker returned 0 clips!');
                            console.log('\n  DIAGNOSIS:');
                            console.log('  - Worker loaded index.json with empty clips array');
                            console.log('  - Worker needs RESTART after index rebuild');
                            console.log('\n  FIX:');
                            console.log('  1. Stop worker (CTRL+C in worker terminal)');
                            console.log('  2. Restart: cd apps/worker && uv run python -m banghack');
                            console.log('  3. Wait for log: "audio_library: 205 clips loaded"');
                            console.log('  4. Refresh dashboard');
                        }
                    } else {
                        console.log('\n  ❌ Command failed');
                        console.log(`  Error: ${msg.error || 'Unknown error'}`);
                    }
                    
                    ws.close();
                    resolve(clips.length);
                }
                
                // Also log other message types for debugging
                if (msg.type === 'hello') {
                    console.log('\n  Received hello from worker');
                    console.log(`  Available commands: ${msg.commands?.length || 0}`);
                }
                
            } catch (e) {
                console.error('  Error parsing message:', e.message);
            }
        });
        
        ws.on('error', (error) => {
            clearTimeout(timeout);
            if (error.code === 'ECONNREFUSED') {
                console.log('\n❌ Connection refused - WORKER NOT RUNNING!');
                console.log('\nSTART WORKER FIRST:');
                console.log('  Terminal 1: cd apps/worker && uv run python -m banghack');
                console.log('  Terminal 2: cd apps/controller && pnpm dev');
                console.log('  Then run this script again');
            } else {
                console.log('\n❌ WebSocket error:', error.message);
            }
            reject(error);
        });
        
        ws.on('close', () => {
            if (!responseReceived) {
                clearTimeout(timeout);
                reject(new Error('Connection closed before receiving response'));
            }
        });
    });
}

// Run test
testAudioList()
    .then((clipCount) => {
        console.log('\n' + '='.repeat(70));
        console.log(`TEST COMPLETE - Found ${clipCount} clips`);
        console.log('='.repeat(70));
        process.exit(0);
    })
    .catch((error) => {
        console.log('\n' + '='.repeat(70));
        console.log('TEST FAILED');
        console.log('='.repeat(70));
        console.error('\nError:', error.message);
        process.exit(1);
    });
