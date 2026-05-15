export interface CompressionResult {
  originalSize: number;
  compressedSize: number;
  savings: string;
  content: string;
  backupPath: string;
}

export class CavemanCompressor {
  private static COMPRESS_PROMPT = `
Compress this markdown into caveman format.

STRICT RULES:
- Do NOT modify anything inside \`\`\` code blocks
- Do NOT modify anything inside inline backticks
- Preserve ALL URLs exactly
- Preserve ALL headings exactly
- Preserve file paths and commands
- Return ONLY the compressed markdown body — do NOT wrap the entire output in a \`\`\`markdown fence or any other fence. Inner code blocks from the original stay as-is; do not add a new outer fence around the whole file.

Only compress natural language.
`;

  async compress(content: string, fileName: string, llmClient: any): Promise<CompressionResult> {
    const originalSize = Buffer.byteLength(content, 'utf8');
    
    const prompt = `${CavemanCompressor.COMPRESS_PROMPT}\n\nTEXT:\n${content}`;
    const compressed = await llmClient.generate(prompt);
    
    const compressedSize = Buffer.byteLength(compressed, 'utf8');
    const savings = (((originalSize - compressedSize) / originalSize) * 100).toFixed(2) + '%';

    return {
      originalSize,
      compressedSize,
      savings,
      content: compressed,
      backupPath: `${fileName}.original.md`
    };
  }

  static stripWrapper(text: string): string {
    return text.replace(/^```markdown\n?/, '').replace(/\n?```$/, '').trim();
  }
}
