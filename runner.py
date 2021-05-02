from relaxER import MatchingRules

matching_rules = MatchingRules(directory_path="dataset/BeerAdvo-RateBeer")
#matching_rules = MatchingRules(directory_path="dataset/iTunes-Amazon")
#matching_rules = MatchingRules(directory_path="dataset/Fodors-Zagats")
#matching_rules = MatchingRules(directory_path="dataset/DBLP-Scholar")
#matching_rules = MatchingRules(directory_path="dataset/DBLP-ACM")

# Esecuzione di RelaxER con 30 coppie iniziali casuali e 5 iterazioni di Active Learning
rule_repository = matching_rules.run_discovery(initial_pairs="train.csv", random_start=True, read_oracle=True, verbose=True)

rule_repository.show_rules()
matching_rules.run_eval(rule_repository)