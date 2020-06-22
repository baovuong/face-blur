import sys 
import argparse 

from hide_faces import hide_faces 

def main():

    cascades = [
        'data/haarcascades/haarcascade_profileface.xml',
        'data/haarcascades/haarcascade_frontalface_default.xml',
        'data/lbpcascades/lbpcascade_frontalface_improved.xml'
    ]

    parser = argparse.ArgumentParser(description='hide some face')
    parser.add_argument('input', help='input filename')
    parser.add_argument('output', help='output filename')
    args = parser.parse_args()
    hide_faces(args.input, args.output, cascades)

if __name__ == '__main__':
    main() 