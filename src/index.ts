import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { SessionManager, KernelManager } from '@jupyterlab/services';
// import { Kernel } from '@jupyterlab/services';
import { IKernelStatusModel } from '@jupyterlab/apputils';
// import { KernelError, Notebook, NotebookActions } from '@jupyterlab/notebook';

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
  requires: [IKernelStatusModel],
  activate: async (app: JupyterFrontEnd, kernel: IKernelStatusModel) => {
    console.log('JupyterLab extension titanoboa-jupyterlab-extension is activated!', {
        frontEnd: app, kernel
    });

    const kernelManager = new KernelManager();
    kernelManager.runningChanged.connect((_, data) => {
      console.log('runningChanged', data);
      data.forEach(model => {

        const conn = kernelManager.connectTo({ model });
        conn.connectionStatusChanged.connect((_, data) => {
          console.log('connectionStatusChanged', data);
        });
        conn.registerCommTarget('test_comm', async (...msg) => {
          console.log("test_comm called after change", msg);
        });
      })
    });
    const sessionManager = new SessionManager({ standby: 'never', kernelManager });

    console.log("kernels", await kernelManager.ready);
    console.log("kernelManager", kernelManager);
    console.log("sessionManager", sessionManager);
    const kernels = Array.from(kernelManager.running()).map(model => kernelManager.connectTo({ model }));
    kernels[0].registerCommTarget('test_comm', async (...msg) => {
        console.log("test_comm called", msg);
        // console.log("ENTER 2", comm);
        // console.log("ENTER 3", msg.content.data);
        // setTimeout(() => {
        //     comm.send({"success": "hello", "echo": msg.content.data});
        //     comm.close();
        //     console.log(comm);
        // }, 350);
    });

    console.log("kernels", kernels);
    // console.log('connect', app.serviceManager.events.stream.connect((_, data) => console.log('event', JSON.stringify(data))));
    console.log('terminals', Array.from(app.serviceManager.terminals.running()));

    // Initialize ethers
    const provider = new ethers.BrowserProvider(window.ethereum);

    // check that we have a signer for this account
    app.commands.addCommand('get_signer', {
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


    app.commands.addCommand('send_transaction', {
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
