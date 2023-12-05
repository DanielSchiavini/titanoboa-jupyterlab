import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { ICommandPalette } from '@jupyterlab/apputils';

import { requestAPI } from './handler';
import { ethers } from 'ethers';

declare global {
    // noinspection JSUnusedGlobalSymbols
  interface Window {
        ethereum: ethers.Eip1193Provider;
    }
}

/**
 * Initialization data for the titanoboa-jupyterlab-extension extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'titanoboa-jupyterlab-extension:plugin',
  description: 'A JupyterLab extension for integrating with the Vyper programming language by using Titanoboa.',
  autoStart: true,
  requires: [ICommandPalette],
  activate: ({ commands, ...rest }: JupyterFrontEnd, palette: ICommandPalette) => {
    console.log('JupyterLab extension titanoboa-jupyterlab-extension is activated!', {
        frontEnd: { ...rest, commands },
    });

    // Initialize ethers
    const provider = new ethers.BrowserProvider(window.ethereum);

    // check that we have a signer for this account
    commands.addCommand('get_signer', {
      label: 'Get Signer',
      execute: async (msg) => {
          console.log("get_signer called", msg);
          const account = (msg as any).content.data.account;
          try {
            const signer = await provider.getSigner(account);
              console.log("success", signer)
              // c.send({"success": signer});
          } catch (error) {
              console.error(error);
              // c.send({"error": error});
          }
      },
    });


    commands.addCommand('send_transaction', {
      label: 'Send Transaction',
      execute: async (msg) => {
          console.log("send_transaction called", msg);
          const tx_data = (msg as any).content.data.transaction_data;
          const account = (msg as any).content.data.account;
          try {
            const signer = await provider.getSigner(account);
            const response = await signer.sendTransaction(tx_data);
              console.log("success", response)
              // c.send({"success": signer});
          } catch (error) {
              console.error(error);
              // c.send({"error": error});
          }
      },
    });

    commands.addCommand('test_comm', {
      label: 'Test Comm',
      execute: async (msg) => {
          console.log("test_comm called", msg);
          // console.log("ENTER 2", comm);
          // console.log("ENTER 3", msg.content.data);
          // setTimeout(() => {
          //     comm.send({"success": "hello", "echo": msg.content.data});
          //     comm.close();
          //     console.log(comm);
          // }, 350);
      },
    });

    requestAPI<any>('get-example')
      .then(data => {
        console.log(data);
      })
      .catch(reason => {
        console.error(
          `The titanoboa_jupyterlab server extension appears to be missing.\n${reason}`
        );
      });
  }
};

export default plugin;
