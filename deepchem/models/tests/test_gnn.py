import os
import pytest
import numpy as np
import deepchem as dc
from deepchem.feat.molecule_featurizers import SNAPFeaturizer


def get_regression_dataset():
    np.random.seed(123)
    featurizer = SNAPFeaturizer()
    dir = os.path.dirname(os.path.abspath(__file__))

    input_file = os.path.join(dir, 'assets/example_regression.csv')
    loader = dc.data.CSVLoader(tasks=["outcome"],
                               feature_field="smiles",
                               featurizer=featurizer)
    dataset = loader.create_dataset(input_file)
    metric = dc.metrics.Metric(dc.metrics.mean_absolute_error,
                               mode="regression")
    return dataset, metric


def compare_weights(key, model1, model2):
    import torch
    return torch.all(
        torch.eq(model1.components[key].weight,
                 model2.components[key].weight)).item()


@pytest.mark.torch
def test_GNN_edge_pred():
    """Tests the unsupervised edge prediction task"""
    from deepchem.models.torch_models.gnn import GNNModular

    dataset, _ = get_regression_dataset()
    model = GNNModular(task="edge_pred")
    loss1 = model.fit(dataset, nb_epoch=5)
    loss2 = model.fit(dataset, nb_epoch=5)
    assert loss2 < loss1


@pytest.mark.torch
def test_GNN_save_reload():
    from deepchem.models.torch_models.gnn import GNNModular

    dataset, _ = get_regression_dataset()
    model = GNNModular(task="edge_pred")
    model.fit(dataset, nb_epoch=1)
    model2 = GNNModular(task="edge_pred")
    model2.load_from_pretrained(model_dir=model.model_dir)
    assert model.components.keys() == model2.components.keys()
    keys_with_weights = [key for key in model.components.keys() if hasattr(model.components[key], 'weight')]
    assert all(compare_weights(key, model, model2) for key in keys_with_weights)
