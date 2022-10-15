from typing import Optional

from pygls.lsp.methods import (
    INITIALIZE,
    TEXT_DOCUMENT_DID_CHANGE,
    TEXT_DOCUMENT_DID_OPEN,
)
from pygls.lsp.types import (
    DidChangeTextDocumentParams,
    DidOpenTextDocumentParams,
    InitializeParams,
)

from . import dump

from .custom import CUSTOM_SERVER_CONFIG_COMMAND
from .custom import config as custom_config
from .custom.features import Features as CustomFeatures
from .server import CustomLanguageServer

server = CustomLanguageServer()


@server.feature(INITIALIZE)
def on_initialize(params: InitializeParams):
    """
    The initialize request is sent as the first request from the client to the server.

    `params` notable/illustrative fields (non-exhaustive):
    ```
    {
        process_id: Optional[int]
        root_uri: Optional[str]
        capabilities: {
            workspace: Optional[WorkspaceClientCapabilities]
            text_document: Optional[TextDocumentClientCapabilities {
                completion: Optional[CompletionClientCapabilities {
                    dynamic_registration: Optional[bool]
                    completion_item: Optional[CompletionItemClientCapabilities]
                    completion_item_kind: Optional[CompletionItemKindClientCapabilities]
                    context_support: Optional[bool]
                }]
                hover: Optional[HoverClientCapabilities]
                signature_help: Optional[SignatureHelpClientCapabilities]
                declaration: Optional[DeclarationClientCapabilities]
                definition: Optional[DefinitionClientCapabilities]
                type_definition: Optional[TypeDefinitionClientCapabilities]
                implementation: Optional[ImplementationClientCapabilities]
                references: Optional[ReferenceClientCapabilities]
                document_highlight: Optional[DocumentHighlightClientCapabilities]
                document_symbol: Optional[DocumentSymbolClientCapabilities]
                code_action: Optional[CodeActionClientCapabilities]
                code_lens: Optional[CodeLensClientCapabilities]
                ...
            }]
            window: Optional[WindowClientCapabilities]
            general: Optional[GeneralClientCapabilities]
            ...
        }
        client_info: Optional[{
            name: str
            version: Optional[str]
        }]
        locale: Optional[str]
        root_path: Optional[str]
        initialization_options: Optional[Any]
        trace: Optional[Trace]
        workspace_folders: Optional[List[ WorkspaceFolder {
            uri: str
            name: str
        }]]
    }
    ```

    https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#initialize
    """
    server.initialize(params)


@server.feature(TEXT_DOCUMENT_DID_CHANGE)
async def did_change(ls: CustomLanguageServer, params: DidChangeTextDocumentParams):
    """
    The document change notification is sent from the client to the server to signal
    changes to a text document.

    `params` notable/illustrative fields (non-exhaustive):
    ```
        {
            text_document: VersionedTextDocumentIdentifier {
                uri: str
                language_id: str
                version: NumType
                text: str
                ...
            }
            content_changes: ...
            ...
        }
    ```

    https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#textDocument_didChange
    """
    CustomFeatures.did_change(ls, params)


@server.feature(TEXT_DOCUMENT_DID_OPEN)
async def did_open(ls: CustomLanguageServer, params: DidOpenTextDocumentParams):
    """
    The document open notification is sent from the client to the server to signal
    newly opened text documents. The document’s content is now managed by the client
    and the server must not try to read the document’s content using the document’s Uri.
    Open in this sense means it is managed by the client. It doesn’t necessarily mean
    that its content is presented in an editor. An open notification must not be sent
    more than once without a corresponding close notification send before. This means
    open and close notification must be balanced and the max open count for a particular
    textDocument is one. Note that a server’s ability to fulfill requests is independent
    of whether a text document is open or closed.

    `params` notable/illustrative fields (non-exhaustive):
    ```
        {
            text_document: TextDocumentItem {
                uri: str
                language_id: str
                version: NumType
                text: str
                ...
            }
            ...
        }
    ```

    https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#textDocument_didOpen
    """
    CustomFeatures.did_open(ls, params)


@server.command(CUSTOM_SERVER_CONFIG_COMMAND)
def show_configuration(
    ls: CustomLanguageServer, *args
) -> Optional[custom_config.InitializationOptions]:
    """
    Returns the server's configuration.

    This is not an officially supported part of LSP. It's just an example of how
    you can create your own LSP server commands. It's not obvious how this is useful
    because generally speaking you don't have control over an editor's LSP client,
    such that you would ever send this command to the server.

    It is however useful for end to end tests, to make sure that the LSP server made
    a basic successful startup.
    """
    config = ls.configuration
    ls.logger.debug("%s: %s", CUSTOM_SERVER_CONFIG_COMMAND, dump(config))

    return config