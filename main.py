import logging
import sys
from datetime import datetime
from os import path
from layoutfreezer import helpers, app


##########  Global Properties  ####################

main_config = {}
main_config["start_time"] = datetime.now()
main_config["root_dir"] = helpers.get_root_dir()


##################   Functions  ###################

def init():
    # load config from file config.yml
    global main_config
    main_config_filepath = path.realpath(
        path.join(main_config["root_dir"], "config.yml"))
    errormessage = f'LayoutFreezer failed to start.\n'

    try:
        main_config.update(
            helpers.load_config_yml(
                config_file_path=main_config_filepath,
                log=False
            )
        )
    except Exception as e:
        errormessage += f'Reason: Failed to load main config.\n'
        errormessage += f'Exception: {e}'
        helpers.errpopup(errormessage=errormessage, level='critical')
        sys.exit()

    main_config = helpers.dict_replace_placeholders(main_config)

    # setup logger    
    try:
        helpers.setup_logger(
            logger_config_path=main_config["logger_config"].replace('@root_dir@', main_config["root_dir"]),
            start_time=main_config["start_time"]
        )
        global logger
        logger = logging.getLogger(__name__)
        logger.info('Logger is up!')
    except Exception as e:
        errormessage += f'Reason: Failed to setup logger.\n'
        errormessage += f'Exception: {e}'
        helpers.errpopup(errormessage=errormessage, level='critical')
        sys.exit()


##########  Main  #################################

if __name__ == "__main__":

    # run init
    init()

    # invoke main program
    try:
        
        
        #TODO remove: 
        print(main_config)
        print('done')

        # invoke main program
        logger.info('Starting application')
        # preferences_path = main_config['layout']['preferences_path']
        app.run(main_config)
        # pass
    except Exception as e:
        try:
            #layoutfreezer.helpers.errpopup(e)
            print(f'(!){e}')
            logger.exception(e)
        except:
            pass
        raise e
