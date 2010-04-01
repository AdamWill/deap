#    This file is part of EAP.
#
#    EAP is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of
#    the License, or (at your option) any later version.
#
#    EAP is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with EAP. If not, see <http://www.gnu.org/licenses/>.

"""The :mod:`toolbox` module is intended to contain the operators that you need
in your evolutionary algorithms, from initialisation to evaluation. It is
always possible to use directly the operators from this module but the toolbox
does also contain the default values of the different parameters for each
method. More over, it makes your algorithms easier to understand and modify,
since once an oprerator is set, it can be reused with a simple keyword that
conatins all its arguments. Plus, every keyword or argument can be overriden
at all time.

The toolbox is also used in predefined algorithms from the :mod:`~eap.algorithms`
module.
"""

import copy
import math
import random
from functools import partial

import eap.base as base

class Toolbox(object):
    """A toolbox for evolution that contains the evolutionary operators.
    At first this toolbox is empty, you can populate it by using the method
    :meth:`register`.
    """

    def register(self, methodName, method, *args, **kargs):
        """Register an operator in the toolbox."""
        setattr(self, methodName, partial(method, *args, **kargs))

    def unregister(self, methodName):
        """Unregister an operator from the toolbox."""
        delattr(self, methodName)


######################################
# GA Crossovers                      #
######################################

def twoPointsCx(ind1, ind2):
    """Execute a two points crossover on the input individuals. The two children
    produced are returned as a tuple, the two parents are left intact.
    This operation apply on an :class:`~eap.base.Individual` composed of a list
    of attributes and act as follow ::
    

        >>> ind1 = [A(1), ..., A(n), ..., A(n+i), ..., A(m)]
        >>> ind2 = [B(1), ..., B(n), ..., B(n+i), ..., B(k)]
        >>> # Crossover with mating points n and n+i, n > 1 and n+i <= min(m, k)
        >>> child1, child2 = twoPointsCx(ind1, ind2)
        >>> print child1
        [A(1), ..., B(n), ..., B(n+i-1), A(n+i), ..., A(m)]
        >>> print child2
        [B(1), ..., A(n), ..., A(n+i-1), B(n+i), ..., B(k)]

    This function use the :func:`~random.randint` function from the python base
    :mod:`random` module.
    """
    size = min(len(ind1), len(ind2))
    child1, child2 = copy.deepcopy(ind1), copy.deepcopy(ind2)
    cxpoint1 = random.randint(1, size)
    cxpoint2 = random.randint(1, size - 1)
    if cxpoint2 >= cxpoint1:
        cxpoint2 += 1
    else:			# Swap the two cx points
        cxpoint1, cxpoint2 = cxpoint2, cxpoint1
   
    child1[cxpoint1:cxpoint2], child2[cxpoint1:cxpoint2] \
         = child2[cxpoint1:cxpoint2], child1[cxpoint1:cxpoint2]
    try:
        child1.fitness.invalidate()
        child2.fitness.invalidate()
    except AttributeError:
        pass
    
    return child1, child2


def onePointCx(indOne, indTwo):
    """Execute a one point crossover on the input individuals. The two children
    produced are returned as a tuple, the two parents are left intact.
    This operation apply on an :class:`~eap.base.Individual` composed of a list
    of attributes and act as follow ::

        >>> ind1 = [A(1), ..., A(n), ..., A(m)]
        >>> ind2 = [B(1), ..., B(n), ..., B(k)]
        >>> # Crossover with mating point n, 1 < n <= min(m, k)
        >>> child1, child2 = twoPointsCx(ind1, ind2)
        >>> print child1
        [A(1), ..., B(n), ..., B(k)]
        >>> print child2
        [B(1), ..., A(n), ..., A(m)]

    This function use the :func:`~random.randint` function from the python base
    :mod:`random` module.
    """
    lSize = min(len(indOne), len(indTwo))
    lChild1, lChild2 = copy.copy(indOne), copy.copy(indTwo)
    lCxPoint = random.randint(1, lSize - 1)
    
    lChild1[lCxPoint:], lChild2[lCxPoint:] = lChild2[lCxPoint:], lChild1[lCxPoint:]
    try:
        lChild1.mFitness.invalidate()
        lChild2.mFitness.invalidate()
    except AttributeError:
        pass
    
    return lChild1, lChild2

def pmCx(ind1, ind2):
    """Execute a partialy matched crossover on the input indviduals. The two
    childrens produced are returned as a tuple, the two parents are left intact.
    This crossover expect individuals of indices, the result for any other type
    of individuals is unpredictable.

    Moreover, this crossover consists of generating two children by matching
    pairs of values in a certain range of the two parents and swaping the values
    of those indexes. For more details see Goldberg and Lingel, "Alleles,
    loci, and the traveling salesman problem", 1985.

    For example, the following parents will produce the two following childrens
    when mated with crossover points ``a = 2`` and ``b = 3``. ::

        >>> ind1 = [0, 1, 2, 3, 4]
        >>> ind2 = [1, 2, 3, 4, 0]
        >>> child1, child2 = pmxCx(ind1, ind2)
        >>> print child1
        [0, 2, 3, 1, 4]
        >>> print child2
        [2, 3, 1, 4, 0]

    This function use the :func:`~random.randint` function from the python base
    :mod:`random` module.
    """
    child1, child2 = copy.deepcopy(ind1), copy.deepcopy(ind2)
    size = min(len(ind1), len(ind2))
    p1, p2 = [0]*size, [0]*size

    # Initialize the position of each indices in the individuals
    for i in xrange(size):
        p1[child1[i]] = i
        p2[child2[i]] = i
    # Choose crossover points
    cxpoint1 = random.randint(0, size)
    cxpoint2 = random.randint(0, size - 1)
    if cxpoint2 >= cxpoint1:
        cxpoint2 += 1
    else:			# Swap the two cx points
        cxpoint1, cxpoint2 = cxpoint2, cxpoint1
    
    # Apply crossover between cx points
    for i in xrange(cxpoint1, cxpoint2):
        # Keep track of the selected values
        temp1 = child1[i]
        temp2 = child2[i]
        # Swap the matched value
        child1[i], child1[p1[temp2]] = temp2, temp1
        child2[i], child2[p2[temp1]] = temp1, temp2
        # Position bookkeeping
        #print lTemp1, lTemp2
        p1[temp1], p1[temp2] = p1[temp2], p1[temp1]
        p2[temp1], p2[temp2] = p2[temp2], p2[temp1]
        #print lPos1

    try:
        child1.fitness.invalidate()
        child2.fitness.invalidate()
    except AttributeError:
        pass
    
    return child1, child2


######################################
# GA Mutations                       #
######################################

def gaussMut(individual, mu, sigma, indpb):
    """This function applies a gaussian mutation on the input individual and
    returns the mutant. The *individual* is left intact and the mutant is an
    independant copy. This mutation expects an iterable individual composed of
    real valued attributes. The *mutIndxPb* argument is the probability of each
    attribute to be mutated.

    .. note::
       The mutation is not responsible for constraints checking, the reason for
       this is that there is too many possibilities for
       resetting the values. For example, if a value exceed the maximum, it may
       be set to the maximum, to the maximum minus (the value minus the maximum),
       it may be cycled to the minimum or even cycled to the minimum plus (the
       value minus the maximum). Wich way is closer to the representation used
       is up to you.
       
       One easy way to add cronstraint checking to an operator is to simply wrap
       the operator in a second function. See the Evolution Strategies example
       for an explicit example.

    This function uses the :func:`~random.random` and :func:`~random.gauss`
    functions from the python base :mod:`random` module.
    """
    lMutated = False
    lIndividual = copy.copy(individual)
    
    for i in xrange(len(lIndividual)):
        if random.random() < indpb:
            lIndividual[i] += random.gauss(mu, sigma)
            if lIndividual[i] < min:
                lIndividual[i] = min
            elif max and lIndividual[i] > max:
                lIndividual[i] = max
            lMutated = True
    if lMutated:
        try:
            lIndividual.mFitness.invalidate()
        except AttributeError:
            pass
    
    return lIndividual


def shuffleIndxMut(individual, indpb):
    """Shuffle the attributes of the input individual and return the mutant.
    The *individual* is left intact and the mutant is an independant copy. The
    *individual* is expected to be iterable. The *shuffleIndxPb* argument is the
    probability of each attribute to be moved.

    This function uses the :func:`~random.random` and :func:`~random.randint`
    functions from the python base :mod:`random` module.
    """
    mutated = False
    mutant = copy.deepcopy(individual)
    
    size = len(mutant)
    for i in range(size):
        if random.random() < indpb:
            swap_indx = random.randint(0, size - 2)
            if swap_indx >= i:
                swap_indx += 1
            mutant[i], mutant[swap_indx] = mutant[swap_indx], mutant[i]
            mutated = True
    if mutated:
        try:
            mutant.fitness.invalidate()
        except AttributeError:
            pass
    
    return mutant


def flipBitMut(individual, indpb):
    """Flip the value of the attributes of the input individual and return the
    mutant. The *individual* is left intact and the mutant is an independant
    copy. The *individual* is expected to be iterable and the values of the
    attributes shall stay valid after the ``not`` operator is called on them.
    The *flipIndxPb* argument is the probability of each attribute to be
    flipped.

    This function uses the :func:`~random.random` function from the python base
    :mod:`random` module.
    """
    mutated = False
    mutant = copy.deepcopy(individual)
    
    for indx in xrange(len(mutant)):
        if random.random() < indpb:
            mutant[indx] = not mutant[indx]
            mutated = True
    if mutated:
        try:
            mutant.fitness.invalidate()
        except AttributeError:
            pass
    
    return mutant

######################################
# GP Crossovers                      #
######################################

def uniformOnePtTreeCx(ind1, ind2):

    child1, child2 = copy.deepcopy(ind1), copy.deepcopy(ind2)
    
    try:
        index = random.randint(1,min([ind1.count_nodes(), ind2.count_nodes()])-1)    
    except ValueError:
        return child1, child2

    sub1 = ind1.search_subtree_dfs(index)
    sub2 = ind2.search_subtree_dfs(index)
    child1.set_subtree_dfs(index, sub2)
    child2.set_subtree_dfs(index, sub1)

    try:
        child1.fitness.invalidate()
        child2.fitness.invalidate()
    except AttributeError:
        pass
    return child1, child2

######################################
# GP Mutations                       #
######################################

def uniformTreeMut(ind, expression, min, max):

    mutant = copy.deepcopy(ind)
    index = random.randint(1, mutant.count_nodes()-1)
    subtree = base.Tree(expression(min=min,max=max))
    mutant.set_subtree_dfs(index, subtree)
    try:
        mutant.fitness.invalidate()
    except AttributeError:
        pass
    return mutant

######################################
# Selections                         #
######################################

def rndSel(individuals, n):
    """Select *n* individuals at random from the input *individuals*. The
    list returned contains shallow copies of the input *individuals*.

    .. versionchanged:: 0.3.1a
       Removed random sample without replacement as this is simply a call to
       python"s :func:`~random.sample` function

    This function uses the :func:`~random.choice` function from the
    python base :mod:`random` module.
    """
    return [random.choice(individuals) for i in xrange(n)]


def bestSel(individuals, n):
    """Select the *n* best individuals among the input *individuals*. The
    list returned contains shallow copies of the input *individuals*.
    """
    return sorted(individuals, key=lambda ind : ind.fitness, reverse=True)[:n]


def worstSel(individuals, n):
    """Select the *n* worst individuals among the input *individuals*. The
    list returned contains shallow copies of the input *individuals*.
    """
    return sorted(individuals, key=lambda ind : ind.mFitness)[:n]


def tournSel(individuals, n, tournsize):
    """Select *n* individuals from the input *individuals* using *n*
    tournaments of *tournSize* individuals. The list returned contains shallow
    copies of the input *individuals*.

    This function uses the :func:`~random.choice` function from the python base
    :mod:`random` module.
    """
    chosen = []
    for i in xrange(n):
        chosen.append(random.choice(individuals))
        for j in xrange(tournsize - 1):
            aspirant = random.choice(individuals)
            if aspirant.fitness > chosen[i].fitness:
                chosen[i] = aspirant

    return chosen

######################################
# Replacement Strategies (ES)        #
######################################



######################################
# Migrations                         #
######################################

def ringMig(populations, n, selection, replacement=None, migarray=None,
            sel_kargs=None, repl_kargs=None):
    """Perform a ring migration between the *populations*. The migration first
    select *n* emigrants from each population using the specified *selection*
    operator and then replace *n* individuals from the associated population in
    the *migarray* by the emigrants. If no *replacement*
    operator is specified, the immigrants will replace the emigrants of the
    population, otherwise, the immigrants will replace the individuals selected
    by the *replacement* operator. The migration array, if provided, shall
    contain each population's index once and only once. If no migration array
    is provided, it defaults to a serial ring migration (1 -- 2 -- ... -- n -- 1).
    You may pass keyworded arguments to the two selection operators by giving a
    dictionary to *sel_kargs* and *repl_kargs*.
    """
    if migarray is None:
        migarray = [(i + 1) % len(populations) for i in xrange(len(populations))]
    else:
        for i in xrange(len(migarray)):
            try:
                migarray.index(i) 
            except ValueError:
                raise ValueError, "The migration array shall contain each population once and only once."

    immigrants = [list()] * len(migarray)
    emigrants = [list()] * len(migarray)
    if sel_kargs is None:
        sel_kargs = {}
    if repl_kargs is None:
        repl_kargs = {}

    for from_deme in xrange(len(migarray)):
        emigrants[from_deme].extend(selection(populations[from_deme], n=n,
                                     **sel_kargs))
        if replacement is None:
            # If no replacement strategy is selected, replace those who migrate
            immigrants[from_deme] = emigrants[from_deme]
        else:
            # Else select those who will be replaced
            immigrants[from_deme].extend(replacement(populations[from_deme],
                                          n=n, **repl_kargs))

    mig_buf = emigrants[0]
    for from_deme, to_deme in enumerate(migarray[1:]):
        from_deme += 1  # Enumerate starts at 0

        for i, immigrant in enumerate(immigrants[to_deme]):
            indx = populations[to_deme].index(immigrant)
            populations[to_deme][indx] = emigrants[from_deme][i]

    to_deme = migarray[0]
    for i, immigrant in enumerate(immigrants[to_deme]):
        indx = populations[to_deme].index(immigrant)
        populations[to_deme][indx] = mig_buf[i]

