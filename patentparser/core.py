import re
import nltk

#Download NLTK modules if not already present
#nltk.download("punkt")
#nltk.download("stopwords")
#nltk.download("averaged_perceptron_tagger")

def traverse(t, np=False):
    try:
        t.label()
    except AttributeError:
        # This is then a tuple e.g. ('A', 'DT') which is a leaf of the tree
        if np:
            print(t[0], end=" ")
    else:
        # Now we know that t.node is defined
        if "S" in t.label():
            for child in t:
                traverse(child)
        elif "NP" in t.label():
            for child in t:
                traverse(child, np=True)
            print("")

class Claim:
    """ Object to model a patent claim."""

    def __init__(self, claimstring):
        """ Initiate claim object with string containing claim text."""
        # Load text
        self.text = claimstring
        # Check for and extract claim number
        self.number, self.text = self.get_number()
        # Get category
        self.category = self.detect_category()
        # Get dependency
        self.dependency = self.detect_dependency()
        
        # Tokenise text into words
        self.words = nltk.word_tokenize(self.text)
        # Label parts of speech - uses averaged_perceptron_tagger as downloaded above
        self.pos = nltk.pos_tag(self.words)
        
        #Split claim into features
        self.features = self.split_into_features()
    
    def nouns(self):
        """ Return the nouns from the claim."""
        return [word for word, part in self.pos if "NN" in part]
    
    def get_number(self):
        """Extracts the claim number from the text."""
        p = re.compile('\d+\.')
        located = p.search(self.text)
        if located:
            # Set claim number as digit before fullstop
            number = int(located.group()[:-1])
            text = self.text[located.end():].strip()
        else:
            number = None
            text = self.text
        return number, text
    
    def detect_category(self):
        """Attempts to determine and return a string containing the claim category."""
        p = re.compile('(A|An|The)\s([\w-]+\s)*(method|process)\s(of|for)?')
        located = p.search(self.text)
        # Or store as part of claim object property?
        if located:
            return "method"
        else:
            return "system"
    
    def determine_entities(self):
        """ Determines noun entities within a patent claim."""
        # Define grammar for chunking
        grammar = '''
            NP: {<DT|PRP\$> <VBG> <NN.*>+} 
                {<DT|PRP\$> <NN.*> <POS> <JJ>* <NN.*>+}
                {<DT|PRP\$>? <JJ>* <NN.*>+ }
            '''
        cp = nltk.RegexpParser(grammar)
        # Or store as part of claim object property?
        
        # Option: split into features / clauses, run over clauses and then re-correlate
        return cp.parse(self.pos)
        
    def print_nps(self):
        ent_tree = self.determine_entities()
        traverse(ent_tree)

    def detect_dependency(self):
        """Attempts to determine if the claim set out in text is dependent - if it is dependency is returned - if claim is deemed independent 0 is returned as dependency """
        p = re.compile('(of|to|with|in)?\s(C|c)laims?\s\d+((\sto\s\d+)|(\sor\s(C|c)laim\s\d+))?(,\swherein)?')
        located = p.search(self.text)
        if located:
            num = re.compile('\d+')
            dependency = int(num.search(located.group()).group())
        else:
            # Also check for "preceding claims" or "previous claims" = claim 1
            pre = re.compile('\s(preceding|previous)\s(C|c)laims?(,\swherein)?')
            located = pre.search(self.text)
            if located:
                dependency = 1
            else:
                dependency = 0
        # Or store as part of claim object property?
        return dependency
        
    def split_into_features(self):
        """ Attempts to split a claim into features.
        param string text: the claim text as a string
        """
        featurelist = []
        startindex = 0
        #split_re = r'(.+;\s*(and)?)|(.+,.?(and)?\n)|(.+:\s*)|(.+\.\s*$)'
        split_expression = r'(;\s*(and)?)|(,.?(and)?\n)|(:\s*)|(\.\s*$)'
        p = re.compile(split_expression)
        for match in p.finditer(self.text):
            feature = {}
            feature['startindex'] = startindex
            endindex = match.end()
            feature['endindex'] = endindex
            feature['text'] = self.text[startindex:endindex]
            featurelist.append(feature)
            startindex = endindex
        # Try spliting on ';' or ',' followed by '\n' or ':'
        #splitlist = filter(None, re.split(r";|(,.?\n)|:", text))
        # This also removes the characters - we want to keep them - back to search method?
        # Or store as part of claim object property?
        return featurelist

class Claimset:
    """ Object to model a claim set. """ 
    
    def extract_claims(text):
        """ Attempts to extract claims as a list from a large text string.
        param string text: string containing several claims
        """
        sent_list = nltk.tokenize.sent_tokenize(text)
        # On a test string this returned a list with the claim number and then the
        # claim text as separate items
        claims_list = [" ".join(sent_list[i:i+2]) for i in xrange(0, len(sent_list), 2)]
        return claims_list

