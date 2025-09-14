import numpy as np
import random

class NeuralNetwork:
    def __init__(self, input_size, hidden_sizes, output_size):
        self.layers = []
        prev_size = input_size

        for hidden_size in hidden_sizes:
            self.layers.append({
                'weights': np.random.randn(prev_size, hidden_size) * 0.5,
                'biases': np.random.randn(hidden_size) * 0.5
            })
            prev_size = hidden_size

        self.layers.append({
            'weights': np.random.randn(prev_size, output_size) * 0.5,
            'biases': np.random.randn(output_size) * 0.5
        })

    def forward(self, inputs):
        x = np.array(inputs)

        for layer in self.layers[:-1]:
            x = np.tanh(np.dot(x, layer['weights']) + layer['biases'])

        # Output layer with sigmoid activation
        final_layer = self.layers[-1]
        x = 1 / (1 + np.exp(-(np.dot(x, final_layer['weights']) + final_layer['biases'])))
        return x

    def get_weights(self):
        weights = []
        for layer in self.layers:
            weights.extend(layer['weights'].flatten())
            weights.extend(layer['biases'].flatten())
        return np.array(weights)

    def set_weights(self, weights):
        idx = 0
        for layer in self.layers:
            w_size = layer['weights'].size
            b_size = layer['biases'].size

            layer['weights'] = weights[idx:idx+w_size].reshape(layer['weights'].shape)
            idx += w_size

            layer['biases'] = weights[idx:idx+b_size].reshape(layer['biases'].shape)
            idx += b_size

    def mutate(self, mutation_rate=0.1, mutation_strength=0.3):
        for layer in self.layers:
            if random.random() < mutation_rate:
                layer['weights'] += np.random.randn(*layer['weights'].shape) * mutation_strength
            if random.random() < mutation_rate:
                layer['biases'] += np.random.randn(*layer['biases'].shape) * mutation_strength

    def copy(self):
        new_nn = NeuralNetwork(0, [], 0)
        new_nn.layers = []
        for layer in self.layers:
            new_nn.layers.append({
                'weights': layer['weights'].copy(),
                'biases': layer['biases'].copy()
            })
        return new_nn

def crossover(parent1, parent2):
    weights1 = parent1.get_weights()
    weights2 = parent2.get_weights()

    crossover_point = random.randint(0, len(weights1))
    child_weights = np.concatenate([weights1[:crossover_point], weights2[crossover_point:]])

    child = parent1.copy()
    child.set_weights(child_weights)
    return child