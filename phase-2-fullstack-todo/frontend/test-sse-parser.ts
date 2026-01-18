// Quick test of SSE parser with user's actual data
import { parseSSEStream } from './lib/sse-parser';

const sampleSSEData = `data: Hey

data: Hey

data:  there

data: !

data: Hey

data:  there

data: !

data:  How

data: Hey

data:  there

data: !

data:  How

data:  can

data:  I

event: done
data: {"thread_id": "2db31cf4-760b-4e04-9b4c-b6614e66bfd2"}

`;

// Test the parser
console.log('Testing SSE Parser with user data...\n');
const chunks = parseSSEStream(sampleSSEData);

console.log('Parsed chunks:');
chunks.forEach((chunk, i) => {
  console.log(`Chunk ${i + 1}:`, JSON.stringify(chunk));
});

console.log('\nCombined text:');
const combinedText = chunks.map(c => c.content).join('');
console.log(combinedText);

console.log('\nExpected: "Hey there ! How can I"');
console.log('Got:', combinedText);
console.log('Match:', combinedText === 'Hey there ! How can I');
