import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { BrowserProvider, ethers, TransactionRequest } from 'ethers';
import { requestAPI } from './handler';


declare global {
  interface Window {
        ethereum: ethers.Eip1193Provider;
        _titanoboa?: {
          loadSigner: (key: string) => Promise<void>;
          signTransaction: (key: string, tx: TransactionRequest) => Promise<void>;
        };
    }
}

const stringify = (data: unknown) => JSON.stringify(data, (_, v) => typeof v === 'bigint' ? v.toString() : v);

/**
 * Initialization data for the titanoboa-jupyterlab-extension extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'titanoboa-jupyterlab-extension:plugin',
  description: 'A JupyterLab extension for integrating with the Vyper programming language by using Titanoboa.',
  autoStart: true,
  activate: async (app: JupyterFrontEnd) => {
    window._titanoboa = {
      loadSigner: async key => {
        console.log('loadSigner');
        const provider = new BrowserProvider(window.ethereum);
        const signer = await provider.getSigner();
        return requestAPI<void>("set_signer", {
          method: "POST",
          body: JSON.stringify({ address: await signer.getAddress(), key }),
        });
      },
      signTransaction: async (key, tx) => {
        const provider = new BrowserProvider(window.ethereum);
        const signer = await provider.getSigner();
        const response = await signer.sendTransaction(tx);
        return requestAPI<void>("send_transaction", {
          method: "POST",
          body: stringify({ ...response, key }),
        });
      },
    };
    console.log('JupyterLab extension titanoboa-jupyterlab-extension is activated!', app, window._titanoboa);
  }
};

export default plugin;
