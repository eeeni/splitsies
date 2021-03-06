import itertools


def find_utilitarian_assignment(bids):
    num_participants = len(bids)
    max_sum = 0
    utilitarian_assignment = None
    for assignment in itertools.permutations(range(num_participants)):
        assignment_sum = 0
        for i, j in enumerate(assignment):
            assignment_sum += bids[i][j]

        if assignment_sum > max_sum:
            utilitarian_assignment = assignment
            max_sum = assignment_sum
    return utilitarian_assignment, max_sum


def generate_assessment_matrix(bids, assignment):
    num_participants = len(bids)
    assessment_matrix = []

    for i in range(num_participants):
        assessment_row = []
        for j in range(num_participants):
            assessment_row.append(compute_assessment(i, j, bids, assignment))
        assessment_matrix.append(assessment_row)

    return assessment_matrix


def compute_assessment(i, j, bids, assignment):
    return bids[i][assignment[j]] - bids[j][assignment[j]]


def run_compensation_round(max_envy):
    envyless_participants = [i for i in max_envy if max_envy[i]['max_envy_amount'] == 0]
    discounts = []
    for i in range(len(max_envy)):
        if i in envyless_participants:
            discounts.append(0)
            continue

        discount_added = False
        for participant in max_envy[i]['max_envy_targets']:
            if participant in envyless_participants:
                discounts.append(max_envy[i]['max_envy_amount'])
                discount_added = True
                break

        if not discount_added:
            discounts.append(0)

    return discounts


def is_envyless(max_envy):
    return max([max_envy[i]['max_envy_amount'] for i in max_envy]) == 0


def get_max_envy(assessment_matrix):
    num_participants = len(assessment_matrix)
    max_envy = {}
    for i in range(num_participants):
        envy_list = [assessment_matrix[i][j] - assessment_matrix[i][i] for j in range(num_participants)]
        max_envy[i] = {'max_envy_amount': max(envy_list),
                       'max_envy_targets': [] if max(envy_list) == 0 else [x for x, y in enumerate(envy_list) if y == max(envy_list)]}
    return max_envy


def update_assessments(assessment_matrix, discounts):
    for i, amt in enumerate(discounts):
        for j in range(len(discounts)):
            assessment_matrix[j][i] += amt
    return assessment_matrix


def check_bids(num_participants, bids, cost):
    assert len(bids) == num_participants
    for i in range(num_participants):
        assert len(bids[i]) == num_participants
        assert sum(bids[i]) == cost


def split_rent(cost, bids):
    num_participants = len(bids)

    check_bids(num_participants, bids, cost)
    total_discounts = num_participants * [0]

    assignment, max_sum = find_utilitarian_assignment(bids)
    surplus = max_sum - cost
    assessment_matrix = generate_assessment_matrix(bids, assignment)
    max_envy = get_max_envy(assessment_matrix)

    while not is_envyless(max_envy):
        discounts = run_compensation_round(max_envy)
        assessment_matrix = update_assessments(assessment_matrix, discounts)
        total_discounts = [sum(x) for x in zip(total_discounts, discounts)]
        max_envy = get_max_envy(assessment_matrix)

    additional_discount = (surplus - sum(total_discounts)) / num_participants
    for i in range(num_participants):
        total_discounts[i] += additional_discount

    final_cost = []
    for i in range(num_participants):
        final_cost.append(bids[i][assignment[i]] - total_discounts[i])

    return assignment, final_cost


def print_results(assignment, final_costs, participants, rooms):
    for i in range(len(assignment)):
        print '{:<10}| {:<15}| ${:<5}'.format(participants[i], rooms[assignment[i]], final_costs[i])

if __name__ == '__main__':
    cost = 3700
    bids = [[928, 728, 730, 718, 0, 0, 596],  #way
            [743, 625, 620, 615, 225, 285, 587],  # elaine
            [824, 676, 677, 677, 0, 0, 846],  #tollers
            [742, 661, 662, 662, 199, 199, 575],  #kopas
            [763, 679, 680, 680, 0, 308, 590],  #jeannie
            [728, 657, 658, 658, 174, 263, 562],  #finleys
            [681, 586, 586, 587, 362, 408, 490]] # almna

    participants = ['Ni', 'Nash', 'Toller', 'Kopa', 'Zuehlke', 'Finley', 'Alma']
    rooms = ['Honeymoon', 'King1', 'King2', 'King3', 'French tub', 'French shower', 'Queen + twin']

    assignment, final_costs = split_rent(cost, bids)
    print_results(assignment, final_costs, participants, rooms)