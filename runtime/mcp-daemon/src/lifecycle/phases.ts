export enum McpLifecyclePhase {
  ConfigLoad = 'config_load',
  ServerRegistration = 'server_registration',
  SpawnConnect = 'spawn_connect',
  InitializeHandshake = 'initialize_handshake',
  ToolDiscovery = 'tool_discovery',
  ResourceDiscovery = 'resource_discovery',
  Ready = 'ready',
  Invocation = 'invocation',
  ErrorSurfacing = 'error_surfacing',
  Shutdown = 'shutdown',
  Cleanup = 'cleanup',
}

export interface McpErrorSurface {
  phase: McpLifecyclePhase;
  serverName?: string;
  message: string;
  context: Record<string, string>;
  recoverable: boolean;
  timestamp: number;
}

export interface McpPhaseResult {
  phase: McpLifecyclePhase;
  status: 'success' | 'failure' | 'timeout';
  duration: number;
  error?: McpErrorSurface;
}

export class McpLifecycleValidator {
  private currentPhase: McpLifecyclePhase | null = null;
  private phaseResults: McpPhaseResult[] = [];

  static validateTransition(from: McpLifecyclePhase | null, to: McpLifecyclePhase): boolean {
    if (!from) return to === McpLifecyclePhase.ConfigLoad;

    const validTransitions: Record<McpLifecyclePhase, McpLifecyclePhase[]> = {
      [McpLifecyclePhase.ConfigLoad]: [McpLifecyclePhase.ServerRegistration],
      [McpLifecyclePhase.ServerRegistration]: [McpLifecyclePhase.SpawnConnect],
      [McpLifecyclePhase.SpawnConnect]: [McpLifecyclePhase.InitializeHandshake],
      [McpLifecyclePhase.InitializeHandshake]: [McpLifecyclePhase.ToolDiscovery],
      [McpLifecyclePhase.ToolDiscovery]: [McpLifecyclePhase.ResourceDiscovery, McpLifecyclePhase.Ready],
      [McpLifecyclePhase.ResourceDiscovery]: [McpLifecyclePhase.Ready],
      [McpLifecyclePhase.Ready]: [McpLifecyclePhase.Invocation, McpLifecyclePhase.Shutdown],
      [McpLifecyclePhase.Invocation]: [McpLifecyclePhase.Ready, McpLifecyclePhase.ErrorSurfacing],
      [McpLifecyclePhase.ErrorSurfacing]: [McpLifecyclePhase.Ready, McpLifecyclePhase.Shutdown],
      [McpLifecyclePhase.Shutdown]: [McpLifecyclePhase.Cleanup],
      [McpLifecyclePhase.Cleanup]: [],
    };

    return (validTransitions[from] || []).includes(to);
  }

  async recordPhase(phase: McpLifecyclePhase, operation: () => Promise<any>): Promise<McpPhaseResult> {
    if (!McpLifecyclePhase.validateTransition(this.currentPhase, phase)) {
      throw new Error(`Invalid MCP lifecycle transition from ${this.currentPhase} to ${phase}`);
    }

    const start = Date.now();
    this.currentPhase = phase;

    try {
      await operation();
      const result: McpPhaseResult = {
        phase,
        status: 'success',
        duration: Date.now() - start
      };
      this.phaseResults.push(result);
      return result;
    } catch (e: any) {
      const error: McpErrorSurface = {
        phase,
        message: e.message || 'Unknown error',
        context: {},
        recoverable: true,
        timestamp: Date.now()
      };
      const result: McpPhaseResult = {
        phase,
        status: 'failure',
        duration: Date.now() - start,
        error
      };
      this.currentPhase = McpLifecyclePhase.ErrorSurfacing;
      this.phaseResults.push(result);
      return result;
    }
  }

  getState() {
    return {
      currentPhase: this.currentPhase,
      results: this.phaseResults
    };
  }
}
