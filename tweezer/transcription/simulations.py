__doc__="""\
Collection of simulations of the transcription process by RNA Polymerases.

References:

:cite:`Ishibashi:2014cd1987:nelson`

.. bibliography:: tweezer.bib

"""


class TranscriptionSimulation(object):
    """
    General container class for simulations of transcription traces.
    """
    def __init__(self):
        self.name = "Transcription Simulation"


class OnlyForwardSimulation(TranscriptionSimulation):
    """
    This simulation assumes that no backtracking occurs and that the RNAP just waits.
    """
    pass


class BacktrackingSimulation(TranscriptionSimulation):
    pass