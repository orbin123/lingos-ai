/**
 * Convert an audio Blob (typically WebM/Opus from MediaRecorder) to a
 * 16-bit PCM WAV Blob using the Web Audio API.
 *
 * Azure Speech SDK only accepts WAV and a handful of compressed formats,
 * **not** WebM. Since browsers record in WebM by default, this helper
 * bridges the gap entirely on the client side — no ffmpeg needed.
 */
export async function blobToWav(blob: Blob): Promise<Blob> {
  const arrayBuffer = await blob.arrayBuffer();
  const AudioCtx =
    window.AudioContext ||
    (window as typeof window & { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;
  const audioContext = new AudioCtx();

  try {
    const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
    return audioBufferToWav(audioBuffer);
  } finally {
    await audioContext.close();
  }
}

function audioBufferToWav(buffer: AudioBuffer): Blob {
  const numChannels = 1; // mono is sufficient for speech
  const sampleRate = buffer.sampleRate;
  const format = 1; // PCM

  // Mix down to mono
  const channelData = buffer.getChannelData(0);
  const samples = new Int16Array(channelData.length);
  for (let i = 0; i < channelData.length; i++) {
    const s = Math.max(-1, Math.min(1, channelData[i]));
    samples[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
  }

  const byteLength = samples.length * 2;
  const headerLength = 44;
  const totalLength = headerLength + byteLength;
  const arrayBuffer = new ArrayBuffer(totalLength);
  const view = new DataView(arrayBuffer);

  // RIFF header
  writeString(view, 0, "RIFF");
  view.setUint32(4, totalLength - 8, true);
  writeString(view, 8, "WAVE");

  // fmt sub-chunk
  writeString(view, 12, "fmt ");
  view.setUint32(16, 16, true); // sub-chunk size
  view.setUint16(20, format, true);
  view.setUint16(22, numChannels, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * numChannels * 2, true); // byte rate
  view.setUint16(32, numChannels * 2, true); // block align
  view.setUint16(34, 16, true); // bits per sample

  // data sub-chunk
  writeString(view, 36, "data");
  view.setUint32(40, byteLength, true);

  // PCM samples
  const output = new Int16Array(arrayBuffer, headerLength);
  output.set(samples);

  return new Blob([arrayBuffer], { type: "audio/wav" });
}

function writeString(view: DataView, offset: number, str: string) {
  for (let i = 0; i < str.length; i++) {
    view.setUint8(offset + i, str.charCodeAt(i));
  }
}
