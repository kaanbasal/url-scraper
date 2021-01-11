import asyncio
import time

from PyInquirer import prompt

from config import Config
from executor import Executor
from graph import Graph
from scraper import Scraper


async def main(_config: Config):
    url = _config.url
    graph = Graph.build(_config.graph_type)
    scraper = Scraper.build(_config.scraper_type)
    executor = Executor.build(_config.executor_type, graph, scraper, url)

    start = time.time()
    await executor.run()
    execution_time = round(time.time() - start, 3)

    print('\n'.join(sorted(graph.all_nodes())))

    print('\n'.join([
        '###########################################',
        f'Graph: {_config.graph_type} | Scraper: {_config.scraper_type} | Executor: {_config.executor_type}\n'
        f'Time to complete: {execution_time} seconds.',
        '###########################################',
    ]))


async def every_config(url: str):
    for graph in Graph.types().keys():
        for scraper in Scraper.types().keys():
            for executor in Executor.types().keys():
                conf = Config(url, graph, scraper, executor)
                await main(conf)


if __name__ == '__main__':
    try:
        answers = prompt([
            {
                'type': 'confirm',
                'name': 'every_config',
                'message': 'Do you want to run all possible configurations?',
            }
        ])

        if answers['every_config']:
            answers = prompt([Config.questions()[0]])

            asyncio.run(every_config(answers['url']))
        else:
            answers = prompt(Config.questions())

            _config = Config.build(answers)

            asyncio.run(main(_config))
    except Exception as e:
        print('\n'.join(['', str(e), '']))

    print('\n')
    input("Press enter to close...")
