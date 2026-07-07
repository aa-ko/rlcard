''' A functional example of training a Deep Monte-Carlo (DMC) agent on
Sechs Nimmt (6 nimmt!) and evaluating it against random opponents.

DMC is a compute-heavy algorithm that is normally trained on a GPU for many
hours. This script runs on CPU by default so it is runnable anywhere; pass
``--cuda 0`` to train on GPU. For a quick end-to-end smoke run, lower
``--total_frames`` (e.g. 5000) and use ``--num_actors 1``; for real training
raise ``--total_frames`` substantially and add more actors.

Examples:
    # Quick CPU smoke run (a couple of learner iterations, then evaluate)
    python examples/run_dmc_sechs_nimmt.py --total_frames 5000 --num_actors 1

    # Longer GPU run
    python examples/run_dmc_sechs_nimmt.py --cuda 0 --total_frames 20000000 \
        --num_actors 5
'''
import os
import argparse

import torch

import rlcard
from rlcard.agents.dmc_agent import DMCTrainer
from rlcard.agents import RandomAgent
from rlcard.utils import get_device, set_seed, tournament


def train(args):
    ''' Train DMC agents (one per seat) via self-play. '''
    env = rlcard.make(args.env, config={'seed': args.seed})

    trainer = DMCTrainer(
        env,
        cuda=args.cuda,
        load_model=args.load_model,
        xpid=args.xpid,
        savedir=args.savedir,
        save_interval=args.save_interval,
        num_actors=args.num_actors,
        total_frames=args.total_frames,
    )

    print('Training DMC on %s for %d frames (cuda=%r, actors=%d)...'
          % (args.env, args.total_frames, args.cuda, args.num_actors))
    trainer.start()


def evaluate(args):
    ''' Load the most recent trained weights for seat 0 and play a tournament
    against random opponents. '''
    device = get_device()
    set_seed(args.seed)
    env = rlcard.make(args.env, config={'seed': args.seed})

    model_dir = os.path.join(args.savedir, args.xpid)
    checkpoints = [f for f in os.listdir(model_dir)
                   if f.startswith('0_') and f.endswith('.pth')] \
        if os.path.isdir(model_dir) else []
    if not checkpoints:
        print('\nNo saved model found in %s to evaluate. Increase '
              '--total_frames or lower --save_interval so a checkpoint is '
              'written.' % model_dir)
        return

    # File names are of the form "0_<frames>.pth"; pick the largest frame count.
    latest = max(checkpoints, key=lambda f: int(f[len('0_'):-len('.pth')]))
    model_path = os.path.join(model_dir, latest)
    # weights_only=False is required: DMCTrainer pickles the entire DMCAgent
    # object (an nn.Module), not just a tensor state_dict, so it cannot be
    # loaded with weights_only=True. Only load checkpoints you trained
    # yourself with this script -- unpickling runs arbitrary code.
    agent = torch.load(model_path, map_location=device, weights_only=False)
    agent.set_device(device)

    agents = [agent] + [RandomAgent(num_actions=env.num_actions)
                        for _ in range(env.num_players - 1)]
    env.set_agents(agents)

    rewards = tournament(env, args.num_eval_games)
    print('\nEvaluation over %d games (loaded %s):' % (args.num_eval_games, latest))
    for position, reward in enumerate(rewards):
        label = 'DMC (trained)' if position == 0 else 'random'
        print('  player %d [%-13s]: mean payoff %+.4f' % (position, label, reward))


if __name__ == '__main__':
    parser = argparse.ArgumentParser("DMC example on Sechs Nimmt in RLCard")
    parser.add_argument('--env', type=str, default='sechs-nimmt',
                        choices=['sechs-nimmt'])
    parser.add_argument('--cuda', type=str, default='',
                        help='CUDA device index, e.g. "0". Empty string = CPU.')
    parser.add_argument('--load_model', action='store_true',
                        help='Resume from an existing checkpoint')
    parser.add_argument('--xpid', default='sechs_nimmt_dmc',
                        help='Experiment id (subdir under --savedir)')
    parser.add_argument('--savedir', default='experiments/dmc_result',
                        help='Root dir where experiment data will be saved')
    parser.add_argument('--save_interval', default=1, type=int,
                        help='Minutes between checkpoint saves')
    parser.add_argument('--num_actors', default=2, type=int,
                        help='Number of actor processes per device')
    parser.add_argument('--total_frames', default=1000000, type=int,
                        help='Total environment frames to train for')
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--num_eval_games', type=int, default=2000)
    parser.add_argument('--skip_eval', action='store_true',
                        help='Train only, do not evaluate afterwards')

    args = parser.parse_args()

    os.environ["CUDA_VISIBLE_DEVICES"] = args.cuda
    train(args)
    if not args.skip_eval:
        evaluate(args)
