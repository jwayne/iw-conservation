from __future__ import division
import time
from conseval.params import ParamDef, Params, WithParams
from conseval.utils.general import norm_scores, window_scores


################################################################################
# Fetch tools
################################################################################

def get_scorer(name, **params):
    """
    Get the appropriate Scorer object in the module scorers.`name`, initialized
    with 'params'.
    """
    scorer_cls = get_scorer_cls(name)
    scorer = scorer_cls(**params)
    return scorer

def get_scorer_cls(name):
    """
    Get the appropriate Scorer class in the module scorers.`name`.
      >>> cls = get_scorer_cls('caprasingh07.js_divergence')
      >>> cls.__module__
      scorers.caprasingh07.js_divergence
      >>> cls.__name__
      JsDivergence
    """
    try:
        scorer_module = __import__('scorers.'+name, fromlist=['x'])
        scorer_clsname = "".join(s.capitalize() for s in name.split('.')[-1].split('_'))
        if hasattr(scorer_module, 'IS_BASE_SCORER'):
            if getattr(scorer_module, 'IS_BASE_SCORER'):
                return 
        scorer_cls = getattr(scorer_module, scorer_clsname)
    except (ImportError, AttributeError), e:
        raise ImportError("%s: %s is not a valid scorer." % (e, name))
    return scorer_cls



################################################################################
# Scorer class
################################################################################

class Scorer(WithParams):
    """
    Base class for any scorer.  Define subclasses that override the _score
    method in scorers/[scorer_name.py] with class name ScorerName.
    """

    # Tunable parameters for scoring.  Children inherit all these parameters
    # along with these defaults.  Defaults can be overridden and parameters
    # can be extended, see scorers/rate4site_eb.py for an example.
    params = Params(
        ParamDef('window_size', 2, int, lambda x: x>=0,
            help="Number of residues on either side included in the window"),
        ParamDef('window_lambda', .5, float, lambda x: 0<=x<=1,
            help="lambda for window heuristic linear combination. Meaningful only if window_size != 0."),
        ParamDef('normalize', False, bool,
            help="return z-scores (over the alignment) of each column, instead of original scores"),
    )


    def __init__(self, **params):
        super(Scorer, self).__init__(**params)
        self.name = ".".join(type(self).__module__.split('.')[1:])


    def score(self, alignment):
        """
        Score each site in the first sequence of `alignment`.  Performs computations
        that are not specific to any site, and calls score_col() to perform the
        site-secific computations.

        Additional global computations can be performed by overriding _precache(),
        see below.

        @param alignment:
            Alignment object
        @return:
            List of scores for each site
        """
        t0 = time.time()

        # Main computation.
        scores = self._score(alignment)

        if self.window_size:
            scores = window_scores(scores, self.window_size, self.window_lambda)
        if self.normalize:
            scores = list(norm_scores(scores, filter=5))

        dt = time.time() - t0 #len(alignment.msa), len(alignment.msa[0])
        return scores


    def _score(self, alignment):
        """
        Called by _score(..).  Override to define scoring method for entire
        alignment.

        @param alignment:
            Alignment object
        @return:
            List of scores for each site
        """
        raise NotImplementedError()


    def set_output_id(self, output_id):
        self.output_id = output_id

    def set_output_dir(self, out_dir):
        self.output_dir = out_dir
