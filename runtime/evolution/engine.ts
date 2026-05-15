import fs from 'fs/promises';
import path from 'path';

export interface EvolutionMutation {
  section: string;
  oldText: string;
  newText: string;
  reasoning: string;
}

export class EvolutionEngine {
  private kernelPath: string;

  constructor(projectDir: string) {
    this.kernelPath = path.join(projectDir, 'runtime/evolution/BUDDY_KERNEL.md');
  }

  async readKernel(): Promise<string> {
    return fs.readFile(this.kernelPath, 'utf8');
  }

  async mutate(mutation: EvolutionMutation): Promise<{ success: boolean; newKernel: string }> {
    const kernel = await this.readKernel();
    
    if (!kernel.includes(mutation.oldText)) {
      throw new Error(`Mutation target not found in kernel: ${mutation.oldText}`);
    }

    const newKernel = kernel.replace(mutation.oldText, mutation.newText);
    await fs.writeFile(this.kernelPath, newKernel);
    
    return { success: true, newKernel };
  }

  async logMutation(mutation: EvolutionMutation): Promise<void> {
    const logPath = path.join(path.dirname(this.kernelPath), 'evolution.log');
    const entry = `[${new Date().toISOString()}] MUTATION: ${mutation.section}\nReason: ${mutation.reasoning}\n---\n`;
    await fs.appendFile(logPath, entry);
  }
}
