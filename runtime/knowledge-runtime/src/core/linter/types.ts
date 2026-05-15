export type Severity = 'error' | 'warning' | 'info';

export interface Finding {
  pass: string;
  severity: Severity;
  path?: string;
  message: string;
  fix?: string;
}

export interface LintContext {
  projectDir: string;
  outputDir: string;
  dbPath: string;
  db?: any;
  validRelations: string[];
  validEntityTypes: string[];
}

export interface LintPass {
  name: string;
  run(ctx: LintContext): Promise<Finding[]>;
  canAutoFix: boolean;
  fix?(ctx: LintContext, findings: Finding[]): Promise<void>;
}

export interface LintResult {
  findings: Finding[];
  passName: string;
  duration: number;
}
