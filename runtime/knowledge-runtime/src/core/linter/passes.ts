import { Finding, LintContext, LintPass } from './types';
import fs from 'fs/promises';
import path from 'path';

export class CompletenessPass implements LintPass {
  name = 'completeness';
  canAutoFix = false;

  async run(ctx: LintContext): Promise<Finding[]> {
    const findings: Finding[] = [];
    const conceptsDir = path.join(ctx.projectDir, ctx.outputDir, 'concepts');
    
    try {
      const entries = await fs.readdir(conceptsDir);
      const existingFiles = new Set(entries.map(e => e.replace('.md', '')));
      const linkRe = /\[\[([^\]]+)\]\]/g;

      for (const file of entries) {
        if (!file.endsWith('.md')) continue;
        const content = await fs.readFile(path.join(conceptsDir, file), 'utf8');
        let match;
        while ((match = linkRe.exec(content)) !== null) {
          const target = match[1];
          if (!existingFiles.has(target)) {
            findings.push({
              pass: this.name,
              severity: 'warning',
              path: path.join(ctx.outputDir, 'concepts', file),
              message: `broken [[${target}]] — no article exists`
            });
          }
        }
      }
    } catch (e) {
      // concepts dir might not exist yet
    }

    return findings;
  }
}

export class OrphansPass implements LintPass {
  name = 'orphans';
  canAutoFix = false;

  async run(ctx: LintContext): Promise<Finding[]> {
    const findings: Finding[] = [];
    if (!ctx.db) return findings;

    // In a real impl, this would query the relations table for nodes with 0 edges
    // Simplified for demo: we assume the DB has a helper or we run a raw query
    try {
      const orphans = await ctx.db.query("SELECT name FROM entities WHERE id NOT IN (SELECT source_id FROM relations UNION SELECT target_id FROM relations) AND type != 'source'");
      for (const row of orphans) {
        findings.push({
          pass: this.name,
          severity: 'info',
          message: `orphan entity ${row.name} — no relations`
        });
      }
    } catch (e) {
      console.error('Orphans pass DB error:', e);
    }

    return findings;
  }
}
