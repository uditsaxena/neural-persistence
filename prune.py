from tqdm import tqdm
import torch
import numpy as np

def prune_loop(model, loss, pruner, dataloader, device, sparsity, 
               schedule, scope, epochs, reinitialize=False, train_mode=False,
               save_pruned_models=False, save_path=""):
    r"""Applies score mask loop iteratively to a final sparsity level.
    """
    # Set model to train or eval mode
    model.train()
    if not train_mode:
        model.eval()

    # Prune model
    for epoch in tqdm(range(epochs)):
        if save_pruned_models:
            torch.save(model.state_dict(), save_path+ "/%s_pruned.pth" % (str(epoch)))
        pruner.score(model, loss, dataloader, device)
        if schedule == 'exponential':
            sparse = sparsity**((epoch + 1) / epochs)
        elif schedule == 'linear':
            sparse = 1.0 - (1.0 - sparsity)*((epoch + 1) / epochs)
        pruner.mask(sparse, scope)
    
    # Reainitialize weights
    if reinitialize:
        model._initialize_weights()

    # Confirm sparsity level
    remaining_params, total_params = pruner.stats()
    if np.abs(remaining_params - total_params*sparsity) >= 5:
        print("ERROR: {} prunable parameters remaining, expected {}".format(remaining_params, total_params*sparsity))
        quit()
