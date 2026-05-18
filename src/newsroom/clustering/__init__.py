"""Story clustering for daily article candidates.

M2 component. Article candidates are grouped into StoryCluster instances
by title-token Jaccard similarity plus shared entity terms. The current
implementation is O(N^2) and intended for daily batches of well under a
thousand articles; scale-up belongs to a later milestone.
"""
