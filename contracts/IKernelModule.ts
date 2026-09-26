export interface IKernelContext {
  readonly runtimeId: string;
  readonly config: Record<string, unknown>;
  readonly services: Record<string, unknown>;
  readonly state: Record<string, unknown>;
  readonly logger: {
    debug(message: string, ...args: unknown[]): void;
    info(message: string, ...args: unknown[]): void;
    warn(message: string, ...args: unknown[]): void;
    error(message: string, ...args: unknown[]): void;
  };
}

export interface IKernelModule {
  readonly name: string;
  readonly version: string;
  readonly description?: string;

  initialize?(context: IKernelContext): Promise<void> | void;
  start?(context: IKernelContext): Promise<void> | void;
  stop?(reason?: string): Promise<void> | void;
  healthCheck?(): Promise<boolean> | boolean;
}
