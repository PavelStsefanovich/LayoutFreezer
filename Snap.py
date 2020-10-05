import logging

from datetime import datetime
from snap import helpers



##########  Global Properties  ####################

global main_config, logger
main_config = {}
main_config["start_time"] = datetime.now()
main_config["timestamp"] = main_config["start_time"].strftime("%Y-%m-%d_%H-%M-%S")
main_config["root_dir"] = helpers.get_root_dir()
main_config["config_dir"] = helpers.join_path(main_config["root_dir"], 'config')



##################   Functions  ###################

def init():
    # setup logger
    try:
        helpers.setup_logger(
            logger_config_path=helpers.join_path(main_config["config_dir"], 'logger.json'),
            timestamp = main_config["timestamp"])
        logger = logging.getLogger(__name__)
        logger.info('Logger is up!')
    except:
        print('(!) ERROR: Failed to setup logger (!)')
        raise

    # load main config
    logger.info('Loading main config')
    main_config.update(config_file_path=helpers.load_config_yml(
        helpers.join_path(main_config["config_dir"], "main.yml")))



##########  Main  #################################

if __name__ == "__main__":

    # invoke main program
    try:
        # run init
        init()
        #TODO remove: 
        print(main_config)
        print('done')

        # invoke main program
        # logger.info('Starting application')
        # preferences_path = main_config['layout']['preferences_path']
        # snap.main.run(main_config, preferences_path)
        # pass
    except Exception as e:
        try:
            #snap.helpers.errpopup(e)
            print(f'(!){e}')
            logger.exception(e)
        except:
            pass
        raise e
