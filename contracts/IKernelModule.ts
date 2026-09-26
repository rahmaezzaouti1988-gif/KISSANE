export interface IKernelModule {
  readonly id: string;
  start(): Promise<void>;
  stop(): Promise<void>;
}
