import { Finding, LintContext, LintPass, LintResult } from './types';
import fs from 'fs/promises';
import path from 'path';

export class KnowledgeLinter {
  constructor(private passes: LintPass[]) {}

  async run(ctx: LintContext, passName?: string, fix = false): Promise<LintResult[]> {
    const results: LintResult[] = [];

    for (const pass of this.passes) {
      if (passName && pass.name !== passName) continue;

      const start = Date.now();
      
      try {
        const findings = await pass.run(ctx);
        const duration = Date.now() - start;

        if (fix && pass.canAutoFix && findings.length > 0 && pass.fix) {
          await pass.fix(ctx, findings);
        }

        results.push({
          findings,
          passName: pass.name,
          duration
        });
      } catch (e) {
        console.error(`Lint pass ${pass.name} failed:`, e);
      }
    }

    return results;
  }

  async saveReport(projectDir: string, results: LintResult[]): Promise<void> {
    const logDir = path.join(projectDir, '.sage', 'lintlog');
    await fs.mkdir(logDir, { recursive: true });

    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    
    const jsonPath = path.join(logDir, `lint-${timestamp}.json`);
    await fs.writeFile(jsonPath, JSON.stringify(results, null, 2));

    let report = '';
    let total = 0;
    for (const r of results) {
      report += `=== ${r.passName} (${r.duration}ms) ===\n`;
      if (r.findings.length === 0) {
        report += '  No issues found.\n';
      } else {
        for (const f of r.findings) {
          report += `  [${f.severity}] ${f.message}${f.path ? ` (${f.path})` : ''}\n`;
          total++;
        }
      }
      report += '\n';
    }
    report += `Total: ${total} findings\n`;

    const txtPath = path.join(logDir, `lint-${timestamp}.txt`);
    await fs.writeFile(txtPath, report);
  }
}
