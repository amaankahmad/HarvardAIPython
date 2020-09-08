import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    # Create list of names in people dict
    names = list(people.keys())
    # Initialise the joint probability
    joint_prob = 1.0

    # Iterate through all the names in data
    for person in names:
        # Calculate the number of GJB2 genes
        genes = get_gene_no(person, one_gene, two_genes)
        # Check if they have trait
        trait = get_have_trait(person, have_trait)

        # Obtain mother and father of person we looking at
        mother = people[person]['mother']
        father = people[person]['father']

        # If person has no parents, use standard gene probability:
        if mother == None and father == None:
            prob = PROBS['gene'][genes]

        # Otherwise need to calculate from parents:
        else:
            # Obtain parent info
            mother_prob = get_parent_prob(mother, one_gene, two_genes)
            father_prob = get_parent_prob(father, one_gene, two_genes)

            # Calculate the probabilities based off parent info
            if genes == 2:
              prob = mother_prob * father_prob
            elif genes == 1:
              prob = (1 - mother_prob) * father_prob + (1 - father_prob) * mother_prob
            else:
              prob = (1 - mother_prob) * (1 - father_prob)

        # Multiply by the probability of the person with x genes having / not having the trait:
        prob *= PROBS['trait'][genes][trait]
        # Apply to the joint probability of dataset
        joint_prob *= prob

    return joint_prob

def get_gene_no(name, one_gene, two_genes):
    """
    joint_probability helper function
    Returns the number of genes of a specific person in dataset.
    Takes:
    - name - the name of the person
    - one_gene - set of people having 1 copy of the gene
    - two_genes - set of people having two copies of the gene.
    """
    # Check if in list of names with 1/2 genes
    if name in one_gene:
        genes = 1
    elif name in two_genes:
        genes = 2
    else:
        genes = 0
    return genes

def get_have_trait(name, have_trait):
    """
    joint_probability helper function
    Returns the boolean of whether the person currently looking at has a trait.
    Takes:
    - name - the name of the person
    - have_trait - set of people having trait of the gene
    """
    # Find out if they have the trait
    if name in have_trait:
        trait = True
    else:
        trait = False    

    return trait

def get_parent_prob(person, one_gene, two_genes):
    """
    joint_probability helper function
    Returns the probability of a parent giving a copy of the mutated gene to their child.
    Takes:
    - person - the name of the parent looking at
    - one_gene - set of people having 1 copy of the gene
    - two_genes - set of people having two copies of the gene.
    """
    # Get number of genes
    parent = get_gene_no(person, one_gene, two_genes)
    # Calculate the probabilities
    if parent == 0:
        return PROBS['mutation']
    elif parent == 1:
        return 0.5
    else:
        return 1 - PROBS['mutation']
    

def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    # Create a list of people in the dictionary
    people = list(probabilities.keys())
    # Iterate through the list of people, adding new joint probability p
    for person in people:
        # Find updates
        genes = get_gene_no(person, one_gene, two_genes)
        trait = get_have_trait(person, have_trait)

        # Add changes to the dictionary
        probabilities[person]['gene'][genes] += p
        probabilities[person]['trait'][trait] += p

def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    # Create a list of people in the dictionary 
    people = list(probabilities.keys())
    # Iterate through the list of people, normalising the triat and genes probabilities
    for person in people:
        # Obtain the total number of probabilities for trait and genes
        total_trait = sum(probabilities[person]['trait'].values())
        total_genes = sum(probabilities[person]['gene'].values())

        # Calculate the normalising factor for trait and gene probabilities
        normal_trait = 1.0/total_trait
        normal_genes = 1.0/total_genes

        # Apply normalisation for trait and gene probabilities
        probabilities[person]['trait'][True] *= normal_trait
        probabilities[person]['trait'][False] *= normal_trait
        for i in range(3):
            probabilities[person]['gene'][i] *= normal_genes

if __name__ == "__main__":
    main()
