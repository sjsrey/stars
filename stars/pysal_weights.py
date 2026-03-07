"""
Adapter layer: STARS spMatrix/spweight ↔ libpysal weights.W
----------------------------------------------------------------------
Phase 1a of STARS modernization plan.

Provides:
  spmatrix_to_w(spmat)  — convert STARS spMatrix → libpysal W
  STARSWeights          — wrap libpysal W with list-indexed interface
                          expected by ProjectWorker (makeGalWeights)
"""

import numpy as np
import libpysal.weights as lpsw


def spmatrix_to_w(spmat):
    """Convert a STARS spMatrix (sparse or full) to a libpysal weights.W.

    Arguments:
        spmat: STARS spMatrix, spGalMatrix, spRegionMatrix, or fMatrix instance.

    Returns:
        w: libpysal weights.W, row-standardized.
    """
    if spmat.matType == "sparse":
        # spmat.dict: {id: [nNeighbors, neighbor_array]}
        neighbors = {k: list(map(int, v[1])) for k, v in spmat.dict.items()}
        # Ensure every obs has an entry even if it has no neighbors
        w = lpsw.W(neighbors, silence_warnings=True)
        w.transform = 'r'
        return w
    else:
        # full matrix: use libpysal full2W
        full = spmat.full()
        w = lpsw.util.full2W(full)
        w.transform = 'r'
        return w


class STARSWeights:
    """Wraps libpysal W to provide the list-indexed interface used by
    ProjectWorker.makeGalWeights / makeGalWeightsAgg.

    Attributes:
        numneigh  — list of neighbor counts, indexed by integer position
        neighbors — list of neighbor-id lists, indexed by integer position
    """

    def __init__(self, w):
        self._w = w
        ids = w.id_order
        self.numneigh = [w.cardinalities[i] for i in ids]
        self.neighbors = [list(w.neighbors[i]) for i in ids]

    @classmethod
    def from_shapefile(cls, filename, wt_type='rook'):
        """Build from a shapefile using libpysal contiguity weights.

        Arguments:
            filename: path to .shp file (with or without extension)
            wt_type:  'rook' (default) or 'queen'
        """
        if wt_type.lower() == 'queen':
            w = lpsw.Queen.from_shapefile(filename, silence_warnings=True)
        else:
            w = lpsw.Rook.from_shapefile(filename, silence_warnings=True)
        return cls(w)

    def fixIslands(self):
        """Attach islands to nearest neighbour using libpysal KNN(k=1) fallback."""
        ids = self._w.id_order
        islands = [i for i in ids if self._w.cardinalities[i] == 0]
        if not islands:
            return
        knn = lpsw.KNN.from_array(
            np.array([[self._w.id_order.index(i)] for i in ids]),
            k=1,
            silence_warnings=True,
        )
        for i in islands:
            j = knn.neighbors[i][0]
            if j not in self._w.neighbors[i]:
                self._w.neighbors[i].append(j)
                self._w.neighbors[j].append(i)
        # Rebuild list caches
        ids = self._w.id_order
        self.numneigh = [len(self._w.neighbors[i]) for i in ids]
        self.neighbors = [list(self._w.neighbors[i]) for i in ids]
