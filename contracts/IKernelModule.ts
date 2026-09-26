export interface IKernelModule {
  readonly id: string;
  readonly name?: string;
  readonly version?: string;
  initialize?(): Promise<void>;
  start(): Promise<void>;
  stop(): Promise<void>;
  shutdown?(): Promise<void>;
}
