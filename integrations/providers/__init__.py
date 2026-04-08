from .blackboard import BlackboardProvider
from .canvas import CanvasProvider


PROVIDER_REGISTRY = {
    "canvas": CanvasProvider,
    "blackboard": BlackboardProvider,
}
