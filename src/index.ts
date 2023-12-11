import { JupyterFrontEndPlugin } from '@jupyterlab/application';
import { BrowserProvider, Eip1193Provider, TransactionRequest } from 'ethers';
import { sendCallback } from './api';

/**
 * Load the signer via ethers user and store it in the backend.
 */
const loadSigner = async (token: string) => {
  console.log("Loading the user's signer");
  const provider = getProvider();
  const signer = await provider.getSigner();
  const address = await signer.getAddress();
  return sendCallback(token, address);
};

/**
 * Sign a transaction via ethers and send it to the backend.
 */
const signTransaction = async (
  token: string,
  transaction: TransactionRequest
) => {
  console.log('Starting to sign transaction');
  const provider = getProvider();
  const signer = await provider.getSigner();
  const response = await signer.sendTransaction(transaction);
  return sendCallback(token, response);
};

declare global {
  // eslint-disable-next-line @typescript-eslint/naming-convention
  interface Window {
    // this variable is injected by the ethers package
    ethereum: Eip1193Provider;
    // this variable is injected by this extension
    _titanoboa?: {
      loadSigner: typeof loadSigner;
      signTransaction: typeof signTransaction;
    };
  }
}

// we delay the initialization of the provider until used
const getProvider = () => new BrowserProvider(window.ethereum);

/**
 * Initialization data for the titanoboa-jupyterlab-extension extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'titanoboa-jupyterlab-extension:plugin',
  description:
    'A JupyterLab extension for integrating with the Vyper programming language by using Titanoboa.',
  autoStart: true,
  /**
   * Activate the extension and register the callbacks that are used by the
   * BrowserSigner to interact with `ethers`.
   */
  activate: () => {
    window._titanoboa = { loadSigner, signTransaction };
    console.log(
      'JupyterLab extension titanoboa-jupyterlab-extension is activated!'
    );
  }
};

export default plugin;
