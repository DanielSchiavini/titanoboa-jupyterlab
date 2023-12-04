import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { requestAPI } from './handler';

/**
 * Initialization data for the titanoboa-jupyterlab-extension extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'titanoboa-jupyterlab-extension:plugin',
  description: 'A JupyterLab extension for integrating with the Vyper programming language by using Titanoboa.',
  autoStart: true,
  activate: (app: JupyterFrontEnd) => {
    console.log('JupyterLab extension titanoboa-jupyterlab-extension is activated!');

    requestAPI<any>('get_example')
      .then(data => {
        console.log(data);
      })
      .catch(reason => {
        console.error(
          `The titanoboa.jupyterlab.extension server extension appears to be missing.\n${reason}`
        );
      });
  }
};

export default plugin;
